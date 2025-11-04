import json
import random
import uuid
from pathlib import Path

OUT = Path("data/generated.jsonl")
NUM_SAMPLES = 200

COMPANIES = [
    ("TechSolutions LLC", "700 Technology Park, San Jose, CA 95110"),
    ("Digital Innovations Corp", "2100 Enterprise Way, Mountain View, CA 94043"),
    ("CloudNet Systems", "1234 Innovation Drive, Palo Alto, CA 94301"),
    ("SecureLogic Inc", "500 Digital Avenue, Sunnyvale, CA 94089"),
    ("Quantum Software Solutions", "888 Tech Boulevard, Santa Clara, CA 95051"),
]

SERVICES = [
    ["Website development and maintenance", "Cloud infrastructure setup", "Security monitoring"],
    ["Software development services", "System integration", "Technical support"],
    ["Data analytics implementation", "API development", "Database management"],
    ["Mobile app development", "DevOps automation", "Cloud migration"],
]

CLAUSE_TYPES = [
    "data_protection",
    "liability",
    "termination",
    "payment",
    "confidentiality",
    "indemnity",
    "warranties",
    "delivery",
]

DATA_PROTECTION_TEMPLATES = [
    "The Provider will retain customer personal data {retention} for analytics and backup purposes.",
    "Customer data collected by the Provider may be shared with affiliates for {purpose}.",
    "The Provider shall ensure appropriate technical and organizational measures to protect personal data, including {measures}.",
]

LIABILITY_TEMPLATES = [
    "The Provider's total liability for any claim shall not exceed the fees paid by the Client in the preceding {months} months.",
    "In no event will either party be liable for indirect, incidental, or consequential damages, including {examples}.",
]

TERMINATION_TEMPLATES = [
    "Either party may terminate this Agreement on {notice} days' written notice to the other party.",
    "This Agreement may be terminated immediately upon material breach which is not cured within {cure_days} days.",
]

PAYMENT_TEMPLATES = [
    "The Client shall pay the Provider {amount} within {days} days of invoice receipt.",
    "Late payments shall accrue interest at {rate}% per annum until paid in full.",
]

CONFIDENTIALITY_TEMPLATES = [
    "Each party shall keep confidential all Confidential Information disclosed by the other party and shall not disclose it to third parties except as required by law.",
    "Confidential Information does not include information that is {exceptions}.",
]

INDEMNITY_TEMPLATES = [
    "The Provider shall indemnify and hold harmless the Client from claims arising out of the Provider's gross negligence or willful misconduct.",
]

WARRANTIES_TEMPLATES = [
    "The Provider warrants that the Services will be performed in a professional and workmanlike manner in accordance with industry standards.",
]

DELIVERY_TEMPLATES = [
    "Provider will deliver the Services in accordance with the schedule set out in Appendix A. Delays due to {causes} are excused.",
]

TEMPLATES = {
    "data_protection": DATA_PROTECTION_TEMPLATES,
    "liability": LIABILITY_TEMPLATES,
    "termination": TERMINATION_TEMPLATES,
    "payment": PAYMENT_TEMPLATES,
    "confidentiality": CONFIDENTIALITY_TEMPLATES,
    "indemnity": INDEMNITY_TEMPLATES,
    "warranties": WARRANTIES_TEMPLATES,
    "delivery": DELIVERY_TEMPLATES,
}

# helper value pools
RETENTION_OPTIONS = ["indefinitely", "2 years", "5 years", "until purpose is fulfilled"]
PURPOSES = ["analytics", "marketing", "service improvement"]
MEASURES = ["encryption at rest", "access controls", "regular audits"]
EXAMPLES = ["loss of profit", "loss of data", "business interruption"]
NOTICE_OPTIONS = ["30", "60", "90"]
AMOUNTS = ["$5,000", "$10,000", "$50,000"]
DAYS = ["14", "30", "45"]
INTEREST_RATES = ["5", "8", "12"]
EXCEPTIONS = ["publicly known", "already in possession of the receiving party", "independently developed"]
CAUSES = ["force majeure events", "third party delays", "regulatory approvals"]


def generate_contract_header():
    # Select two different companies for provider and client
    provider, client = random.sample(COMPANIES, 2)
    services = random.choice(SERVICES)
    
    # Generate dates
    from datetime import datetime, timedelta
    current_date = datetime.now()
    term_months = random.choice([6, 12, 24])
    end_date = current_date + timedelta(days=term_months * 30)
    
    header = f'''SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into on {current_date.strftime("%B %d, %Y")}, between:

{provider[0]}
{provider[1]}
(hereinafter referred to as the "Provider")

and

{client[0]}
{client[1]}
(hereinafter referred to as the "Client")

1. SERVICES
1.1. The Provider agrees to provide the following services:
{chr(10).join(f"- {service}" for service in services)}

2. TERM AND TIMELINE
2.1. Term: {term_months} months from the effective date
2.2. Timeline:
     - Effective Date: {current_date.strftime("%B %d, %Y")}
     - End Date: {end_date.strftime("%B %d, %Y")}

'''
    return header

def render_clause(clause_type):
    header = generate_contract_header() if clause_type == "data_protection" else ""
    tpl = random.choice(TEMPLATES[clause_type])
    # substitute placeholders
    clause = tpl.format(
        retention=random.choice(RETENTION_OPTIONS),
        purpose=random.choice(PURPOSES),
        measures=random.choice(MEASURES),
        examples=random.choice(EXAMPLES),
        months=random.choice(["3", "6", "12"]),
        notice=random.choice(NOTICE_OPTIONS),
        cure_days=random.choice(["7", "14", "30"]),
        amount=random.choice(AMOUNTS),
        days=random.choice(DAYS),
        rate=random.choice(INTEREST_RATES),
        exceptions=random.choice(EXCEPTIONS),
        causes=random.choice(CAUSES),
    )
    return header + clause


def make_completion(clause, clause_type):
    # simple structured completion: Risk level and recommendation(s)
    risk = random.choices(["Low", "Medium", "High"], weights=[0.4, 0.4, 0.2])[0]
    recs = []
    if clause_type == "data_protection":
        if "indefinitely" in clause or "indefinite" in clause:
            risk = "High"
            recs.append("Specify a retention period and purpose limitation.")
        else:
            recs.append("Ensure encryption and access controls are in place.")
    elif clause_type == "liability":
        recs.append("Consider excluding gross negligence and adding insurance requirements.")
    elif clause_type == "termination":
        recs.append("Clarify post-termination obligations such as data return and refunds.")
    elif clause_type == "payment":
        recs.append("Define invoice dispute resolution and late payment remedies.")
    elif clause_type == "confidentiality":
        recs.append("Narrow the definition of Confidential Information and specify return/destruction procedures.")
    elif clause_type == "indemnity":
        recs.append("Limit indemnity to direct damages and require notice and control of defense.")
    elif clause_type == "warranties":
        recs.append("Consider adding disclaimers for third-party components and a specific warranty period.")
    elif clause_type == "delivery":
        recs.append("Add specific milestones, acceptance criteria, and remedies for delays.")

    completion = f"Risk: {risk} - Recommendations: {' '.join(recs)}"
    return completion


def generate(n=NUM_SAMPLES, out=OUT):
    out.parent.mkdir(parents=True, exist_ok=True)
    samples = []
    for i in range(n):
        clause_type = random.choice(CLAUSE_TYPES)
        clause = render_clause(clause_type)
        sample = {
            "id": str(uuid.uuid4()),
            "prompt": f"Analyze the following contract clause for regulatory compliance and recommend fixes:\n\n{clause}",
            "completion": make_completion(clause, clause_type),
            "metadata": {"type": clause_type}
        }
        samples.append(sample)
    with out.open("w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Wrote {len(samples)} synthetic samples to {out}")


if __name__ == "__main__":
    generate()
