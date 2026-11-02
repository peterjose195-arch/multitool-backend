from fastapi import APIRouter, HTTPException, Depends
import httpx
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from database import get_db, LeadAuditRecord

router = APIRouter(prefix="/lead-gen", tags=["Lead Generation"])

@router.get("/verify-and-fetch")
async def verify_and_fetch(target_domain: str, db: Session = Depends(get_db)):
    if not target_domain.startswith("http://") and not target_domain.startswith("https://"):
        target_domain = f"https://{target_domain}"

    parsed = urlparse(target_domain)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_url}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            resp = await client.get(robots_url)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.allow_all = True
    except Exception:
        rp.allow_all = True

    is_allowed = rp.can_fetch("*", target_domain)

    # Record compliance audit
    record = LeadAuditRecord(domain=target_domain, allowed=1 if is_allowed else 0)
    db.add(record)
    db.commit()

    if not is_allowed:
        raise HTTPException(status_code=403, detail="Scraping disallowed by robots.txt")

    return {
        "domain": target_domain,
        "robots_url": robots_url,
        "allowed": True,
        "status": "verified"
    }
  
