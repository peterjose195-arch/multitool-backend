from fastapi import APIRouter, HTTPException, Depends
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import get_db, PriceRecord

router = APIRouter(prefix="/tracker", tags=["Price Tracker"])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

@router.get("/check-price")
async def check_price(
    target_url: str,
    cost_price: float = 0.0,
    selling_price: float = 0.0,
    db: Session = Depends(get_db)
):
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            response = await client.get(target_url, headers=HEADERS)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Target URL unreachable.")

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "Unknown Title"

            # Persist check record to database
            record = PriceRecord(
                url=target_url,
                title=title,
                cost_price=cost_price,
                selling_price=selling_price
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            margin = selling_price - cost_price
            return {
                "id": record.id,
                "url": target_url,
                "title": title,
                "cost_price": cost_price,
                "selling_price": selling_price,
                "margin": round(margin, 2),
                "status": "saved"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_price_history(db: Session = Depends(get_db)):
    records = db.query(PriceRecord).order_by(PriceRecord.created_at.desc()).limit(50).all()
    return records
  
