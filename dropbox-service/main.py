from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import auth, models, database
import aiofiles

database.init_db()
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_db():
    async with database.SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    await database.init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.close_db()

@app.post("/register/")
async def register_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    hashed_password = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed_password)
    try:
        db.add(user)
        await db.commit()
        return {"msg": "User registered successfully"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")

@app.post("/token/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    async with db as session:
        query = await session.execute(select(models.User).where(models.User.username == form_data.username))
        user = query.scalars().first()
        if user and auth.verify_password(form_data.password, user.hashed_password):
            access_token = auth.create_access_token(user.username)
            return {"access_token": access_token, "token_type": "bearer"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    async with aiofiles.open(f"files/{file.filename}", 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    file_record = models.File(filename=file.filename, content_type=file.content_type, content=content)
    db.add(file_record)
    await db.commit()
    return {"filename": file.filename}

@app.get("/files/")
async def get_files_list(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    query = await db.execute(select(models.File))
    files = query.scalars().all()
    return files

@app.get("/download/{file_id}")
async def download_file(file_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    query = await db.execute(select(models.File).where(models.File.id == file_id))
    file = query.scalar()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file.content
