"""Pydantic models for API response validation."""

from pydantic import BaseModel, EmailStr


class Address(BaseModel):
    street: str
    suite: str
    city: str
    zipcode: str


class Company(BaseModel):
    name: str
    catchPhrase: str
    bs: str


class UserModel(BaseModel):
    id: int
    name: str
    username: str
    email: str          # EmailStr requires extra install; str is fine for demo
    address: Address
    phone: str
    website: str
    company: Company


class PostModel(BaseModel):
    id: int
    userId: int
    title: str
    body: str


class CommentModel(BaseModel):
    id: int
    postId: int
    name: str
    email: str
    body: str
