"""
认证相关API端点
提供用户登录、注册、登出等功能
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserPermission
from app.auth import (
    get_password_hash, verify_password,
    create_access_token, oauth2_scheme,
    get_current_user, get_current_active_user,
    get_current_admin, require_role
)
from app.schemas import (
    UserLogin, UserRegister, TokenResponse,
    ResponseModel, ResponseBase
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ResponseModel, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口

    **请求参数：**
    - username: 用户名
    - password: 密码

    **响应示例：**
    ```json
    {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user_info": {
                "id": 1,
                "username": "admin",
                "real_name": "管理员",
                "role": "admin",
                "is_active": 1
            }
        }
    }
    ```
    """
    # 查询用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用"
        )

    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()

    # 创建token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    # 返回响应
    return ResponseModel(
        code=200,
        message="登录成功",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role,
                "is_active": user.is_active
            }
        ).model_dump(exclude_none=True)
    )


@router.post("/register", response_model=ResponseModel, summary="用户注册")
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册接口

    **请求示例：**
    ```json
    {
        "username": "newuser",
        "password": "password123",
        "real_name": "新用户",
        "role": "operator"
    }
    ```

    **响应示例：**
    ```json
    {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": 2,
            "username": "newuser",
            "real_name": "新用户",
            "role": "operator"
        }
    }
    ```
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        role=user_data.role,
        is_active=1
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 初始化用户权限（如果有）
    # TODO: 可以在这里初始化默认权限

    return ResponseModel(
        code=200,
        message="注册成功",
        data={
            "id": new_user.id,
            "username": new_user.username,
            "real_name": new_user.real_name,
            "role": new_user.role,
            "is_active": new_user.is_active
        }
    )


@router.get("/me", response_model=ResponseModel, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户的信息

    **响应示例：**
    ```json
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": 1,
            "username": "admin",
            "real_name": "管理员",
            "role": "admin",
            "is_active": 1,
            "last_login": "2026-04-02T23:30:00"
        }
    }
    ```
    """
    return ResponseModel(
        code=200,
        message="success",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "real_name": current_user.real_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "last_login": current_user.last_login
        }
    )


@router.post("/logout", response_model=ResponseModel, summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出接口

    **说明：**
    - 由于使用JWT无状态认证，登出主要是客户端移除token
    - 服务端可以记录token的黑名单（如果需要）
    """
    return ResponseModel(
        code=200,
        message="登出成功",
        data={"message": "请在前端移除token"}
    )


@router.put("/change-password", response_model=ResponseModel, summary="修改密码")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user)
):
    """
    修改当前用户密码

    **请求参数：**
    - old_password: 旧密码
    - new_password: 新密码（至少6位）

    **响应示例：**
    ```json
    {
        "code": 200,
        "message": "密码修改成功",
        "data": {}
    }
    ```
    """
    # 验证旧密码
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 检查新密码是否与旧密码相同
    if old_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )

    # 更新密码
    current_user.password_hash = get_password_hash(new_password)
    db.commit()

    return ResponseModel(
        code=200,
        message="密码修改成功",
        data={}
    )
