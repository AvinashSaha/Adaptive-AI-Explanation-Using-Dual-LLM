import google.generativeai as genai
from config import Config
import markdown
import re

def parse_citations(citation_text):
    citation_lines = []
    for line in citation_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        url_match = re.search(r"https?://[^\s\)]+", line)
        if url_match:
            url = url_match.group(0)
            citation_lines.append({"text": line, "url": url})
        else:
            citation_lines.append({"text": line, "url": None})
    return citation_lines

class LLMService:
    def __init__(self):
        print("Config.GEMINI1_API_KEY:", Config.GEMINI1_API_KEY[:8], "...")
        print("Config.GEMINI2_API_KEY:", Config.GEMINI2_API_KEY[:8], "...")
        print("Config.GEMINI1_MODEL:", Config.GEMINI1_MODEL)
        print("Config.GEMINI2_MODEL:", Config.GEMINI2_MODEL)
        genai.configure(api_key=Config.GEMINI1_API_KEY)
        self.llm1_model = genai.GenerativeModel(Config.GEMINI1_MODEL)
        genai.configure(api_key=Config.GEMINI2_API_KEY)
        self.llm2_model = genai.GenerativeModel(Config.GEMINI2_MODEL)

    def get_llm1_response(self, question):
        try:
            response = self.llm1_model.generate_content(
                f"Give a brief, practical health tip for: {question}\n"
                "Limit response to 2-3 short sentences. Do NOT provide references or detailed evidence."
            )
            answer_md = response.text
            answer_html = markdown.markdown(answer_md)
            return answer_html
        except Exception as e:
            print("LLM1 error:", str(e))
            return f"<div class='error'>Error generating base answer: {str(e)}</div>"

    def get_llm2_response(self, question, llm1_answer):
        try:
            # Main prompt (forced separation for quote/proof)
            prompt = f"""
You are a clinical research verifier. Your task is to evaluate the following health answer in the manner of a panel of medical experts.

- Identify the main medical claims made in the answer.
- For each claim, consult at least two authoritative sources (NHS, WHO, or respected peer-reviewed medical journals).
- Assess consensus and evidence for each claim.
- Synthesize a consensus explanation, noting agreements/disagreements or uncertainty.
- State a final verdict on accuracy for the answer.

**Respond in this exact structure:**

Verification: [Verified / Partially Verified / Needs Clarification / Incorrect]

Consensus Summary: [Summary of agreements/disagreements among sources.]

Detailed Explanation: [Integrate evidence, reference sources, and explain each claim. “Return the detailed explanation as HTML with a <ul> list, each main point in a separate <li> bullet, not as plain paragraphs.”]

Representative Quote: ["A single direct quote, phrase, or policy language from a top source that best summarizes or supports the answer overall."]

Quoted Proof: ["A separate, specific direct quote from a different reputable source, focusing on a key claim or piece of evidence related to the answer. This should not duplicate the Representative Quote."]

Citation: [Full citation and link for every source referenced, presented one per line.]

**Instructions:**  
- Do not duplicate text between Representative Quote and Quoted Proof.  
- If a section has no available data, output 'N/A' for that section.
- Return only this structure with section labels exactly as above.
- “Return the detailed explanation as HTML with a <ul> list, each main point in a separate <li> bullet, not as plain paragraphs.”

Question: {question}
Answer to verify: {llm1_answer}
"""
            response = self.llm2_model.generate_content(prompt)
            output = response.text.strip()
            print("LLM2 full prompt answer:\n", output)

            keys = [
                "verification",
                "consensus summary",
                "detailed explanation",
                "representative quote",
                "quoted proof",
                "citation"
            ]
            parsed = {key: "" for key in keys}
            for line in output.split('\n'):
                for key in keys:
                    pattern = rf"^{key.replace(' ', '[ \\-_]?').title()}:"
                    if re.match(pattern, line.strip(), re.IGNORECASE):
                        value = line.split(':', 1)[1].strip()
                        parsed[key] = value

            # Fallback extraction for missing fields
            for key in keys:
                if not parsed[key]:
                    search_label = key.replace(' ', '[ \\-_]?').title() + ":"
                    regex = re.compile(rf"{search_label}\s*(.*?)($|\n[A-Z][a-zA-Z ]{{2,}}:)", re.IGNORECASE | re.DOTALL)
                    matches = regex.findall(output)
                    if matches:
                        section_text = matches[0][0].strip()
                        if section_text and section_text.lower() != 'n/a':
                            parsed[key] = section_text

            if not any(parsed.values()):
                parsed["detailed explanation"] = output

            # Add parsed, clickable citation list
            parsed["citations_list"] = parse_citations(parsed["citation"])

            print("LLM2 parsed dict:", parsed)
            return parsed

        except Exception as e:
            print("LLM2 error:", str(e))
            return {
                "verification": "Error",
                "consensus summary": "",
                "detailed explanation": f"Error: {str(e)}",
                "representative quote": "",
                "quoted proof": "",
                "citation": "",
                "citations_list": []
            }
