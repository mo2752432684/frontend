from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schema import Comment, CommentCreate, CommentResponse
from db import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_comment_with_replies(comment: Comment, db: Session) -> CommentResponse:
    replies = db.query(Comment).filter(Comment.parent_id == comment.id).all()
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=[get_comment_with_replies(reply, db) for reply in replies]
    )

@router.post("/comments/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = Comment(
        post_id=comment.post_id,
        user_id=comment.user_id,
        content=comment.content,
        parent_id=comment.parent_id if comment.parent_id != 0 else None
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/comments/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return get_comment_with_replies(comment, db)

@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
def read_comments_for_post(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id, Comment.parent_id == None).all()
    return [get_comment_with_replies(comment, db) for comment in comments]