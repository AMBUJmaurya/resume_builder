import openai
import json
from django.conf import settings
from typing import Dict, List, Any


class AIResumeService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key

    def generate_resume_content(self, job_title: str, years_of_experience: int, 
                              skills: List[str] = None, education_level: str = None,
                              industry: str = None, additional_info: str = None) -> Dict[str, Any]:
        """
        Generate AI-powered resume content based on user input
        """
        if not self.api_key:
            return {"error": "OpenAI API key not configured"}

        try:
            # Build the prompt for AI
            prompt = self._build_resume_prompt(
                job_title, years_of_experience, skills, 
                education_level, industry, additional_info
            )

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer and career coach. Generate professional resume content in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )

            # Parse the response
            content = response.choices[0].message.content
            return self._parse_ai_response(content)

        except Exception as e:
            return {"error": f"AI generation failed: {str(e)}"}

    def _build_resume_prompt(self, job_title: str, years_of_experience: int,
                           skills: List[str] = None, education_level: str = None,
                           industry: str = None, additional_info: str = None) -> str:
        """
        Build a comprehensive prompt for AI resume generation
        """
        prompt = f"""
        Create a professional resume for a {job_title} position with {years_of_experience} years of experience.
        
        Requirements:
        - Job Title: {job_title}
        - Years of Experience: {years_of_experience}
        - Skills: {', '.join(skills) if skills else 'Not specified'}
        - Education Level: {education_level if education_level else 'Not specified'}
        - Industry: {industry if industry else 'Not specified'}
        - Additional Info: {additional_info if additional_info else 'None'}
        
        Please generate the following sections in JSON format:
        1. Professional Summary (2-3 sentences)
        2. 3-4 relevant work experiences with achievements
        3. Education details
        4. Technical skills (categorized)
        5. 2-3 relevant projects
        6. Certifications (if applicable)
        
        Format the response as a valid JSON object with the following structure:
        {{
            "summary": "Professional summary text",
            "experiences": [
                {{
                    "company": "Company name",
                    "position": "Job title",
                    "duration": "Start date - End date",
                    "description": "Job description",
                    "achievements": ["Achievement 1", "Achievement 2", "Achievement 3"]
                }}
            ],
            "education": [
                {{
                    "institution": "University/College name",
                    "degree": "Degree name",
                    "field": "Field of study",
                    "year": "Graduation year"
                }}
            ],
            "skills": {{
                "technical": ["Skill 1", "Skill 2"],
                "soft_skills": ["Skill 1", "Skill 2"],
                "tools": ["Tool 1", "Tool 2"]
            }},
            "projects": [
                {{
                    "title": "Project name",
                    "description": "Project description",
                    "technologies": ["Tech 1", "Tech 2"],
                    "achievements": ["Achievement 1", "Achievement 2"]
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification name",
                    "issuer": "Issuing organization",
                    "year": "Year obtained"
                }}
            ]
        }}
        
        Make the content realistic, professional, and tailored to the job requirements.
        """

        return prompt

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """
        Parse the AI response and return structured data
        """
        try:
            # Try to extract JSON from the response
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                return {"error": "Invalid response format from AI"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response"}

    def enhance_existing_content(self, content: str, section: str) -> str:
        """
        Enhance existing resume content using AI
        """
        if not self.api_key:
            return "OpenAI API key not configured"

        try:
            prompt = f"""
            Enhance the following {section} content for a resume. Make it more professional, 
            impactful, and achievement-oriented. Keep it concise but compelling.
            
            Original content:
            {content}
            
            Please provide the enhanced version:
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer. Enhance the given content to be more professional and impactful."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Enhancement failed: {str(e)}"

    def generate_cover_letter(self, job_title: str, company: str, resume_summary: str) -> str:
        """
        Generate a cover letter based on job details and resume summary
        """
        if not self.api_key:
            return "OpenAI API key not configured"

        try:
            prompt = f"""
            Write a professional cover letter for a {job_title} position at {company}.
            
            Resume Summary:
            {resume_summary}
            
            The cover letter should:
            - Be 3-4 paragraphs
            - Highlight relevant experience and skills
            - Show enthusiasm for the role
            - Be professional and well-structured
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cover letter writer. Create compelling and professional cover letters."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Cover letter generation failed: {str(e)}" 