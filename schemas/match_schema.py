from pydantic import BaseModel, Field

class MatchResult (BaseModel):
    match_score : int = Field(description= 'Match percentage between the candidate profile and JD, from 0 to 100')
    matching_skills : list[str] = Field(description= 'List of matching skills found in the candidate profile')
    missing_skills : list[str] = Field(description= 'List of skills required by JD but missing in candidate profile')
    summary: str = Field(description= 'A brief 3-4 sentence executive summary of candidate fit')
