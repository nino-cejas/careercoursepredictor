import argparse
import re
from itertools import permutations, product

import pandas as pd


CAREER_OPTIONS = [
	{"career": "Civil Engineer", "course": "BS Civil Engineering"},
	{"career": "Marketing Manager", "course": "BS Business Administration Major in Marketing"},
	{"career": "Software Engineer", "course": "BS Computer Science"},
	{"career": "Registered Nurse", "course": "BS Nursing"},
	{"career": "CPA Accountant", "course": "BS Accountancy"},
	{"career": "Psychometrician", "course": "BS Psychology"},
	{"career": "Data Scientist", "course": "BS Statistics"},
	{"career": "Architect", "course": "BS Architecture"},
	{"career": "Licensed Pharmacist", "course": "BS Pharmacy"},
	{"career": "Graphic Designer", "course": "BFA Multimedia Arts"},
	{"career": "Mechanical Engineer", "course": "BS Mechanical Engineering"},
	{"career": "Lawyer / Attorney", "course": "BA Political Science"},
	{"career": "IT Specialist", "course": "BS Information Technology"},
	{"career": "Medical Technologist", "course": "BS Medical Technology"},
	{"career": "Financial Analyst", "course": "BS Business Administration Major in Finance"},
	{"career": "News Journalist", "course": "BA Journalism"},
	{"career": "Electrical Engineer", "course": "BS Electrical Engineering"},
	{"career": "Executive Chef", "course": "BS Culinary Management"},
	{"career": "Veterinarian", "course": "Doctor of Veterinary Medicine"},
	{"career": "HR Manager", "course": "BSBA Human Resource Management"},
	{"career": "Aircraft Mechanic", "course": "BS Aircraft Maintenance Technology"},
	{"career": "Social Worker", "course": "BS Social Work"},
	{"career": "Cybersecurity Analyst", "course": "BS Cybersecurity"},
	{"career": "Microbiologist", "course": "BS Biology"},
	{"career": "Hotel Manager", "course": "BS Hospitality Management"},
	{"career": "Physical Therapist", "course": "BS Physical Therapy"},
	{"career": "Geodetic Engineer", "course": "BS Geodetic Engineering"},
	{"career": "Librarian", "course": "BS Library and Information Science"},
	{"career": "Environmental Planner", "course": "BS Environmental Science"},
	{"career": "Economist", "course": "BS Economics"},
	{"career": "Chemical Engineer", "course": "BS Chemical Engineering"},
	{"career": "Criminologist", "course": "BS Criminology"},
	{"career": "Interior Designer", "course": "BS Interior Design"},
	{"career": "Radiologic Technologist", "course": "BS Radiologic Technology"},
	{"career": "Customs Broker", "course": "BS Customs Administration"},
	{"career": "PR Specialist", "course": "BA Communication"},
	{"career": "Computer Engineer", "course": "BS Computer Engineering"},
	{"career": "Nutritionist-Dietitian", "course": "BS Nutrition and Dietetics"},
	{"career": "Flight Attendant", "course": "BS Tourism Management"},
	{"career": "Real Estate Broker", "course": "BS Real Estate Management"},
	{"career": "Industrial Engineer", "course": "BS Industrial Engineering"},
	{"career": "Agriculturist", "course": "BS Agriculture"},
	{"career": "Marine Biologist", "course": "BS Marine Biology"},
	{"career": "Systems Administrator", "course": "BS Information Systems"},
	{"career": "Occupational Therapist", "course": "BS Occupational Therapy"},
	{"career": "Game Developer", "course": "BS Entertainment & Multimedia Computing"},
	{"career": "Marine Engineer", "course": "BS Marine Engineering"},
	{"career": "Merchant Marine Officer", "course": "BS Marine Transportation"},
	{"career": "Geologist", "course": "BS Geology"},
	{"career": "Actuary", "course": "BS Mathematics"},
	{"career": "Software Tester", "course": "BS Computer Science"},
	{"career": "Preschool Teacher", "course": "Bachelor of Early Childhood Education"},
	{"career": "SPED Teacher", "course": "Bachelor of Special Needs Education"},
	{"career": "High School Teacher", "course": "Bachelor of Secondary Education"},
	{"career": "Mining Engineer", "course": "BS Mining Engineering"},
	{"career": "Petroleum Engineer", "course": "BS Petroleum Engineering"},
	{"career": "Forensic Investigator", "course": "BS Forensic Science"},
	{"career": "Bank Manager", "course": "BSBA Banking and Finance"},
	{"career": "Operations Manager", "course": "BSBA Operations Management"},
	{"career": "UI/UX Designer", "course": "BS Information Technology"},
	{"career": "App Developer", "course": "BS Computer Science"},
	{"career": "Radio/TV Broadcaster", "course": "BA Broadcasting"},
	{"career": "Fashion Designer", "course": "BS Fashion Design and Technology"},
	{"career": "Optometrist", "course": "Doctor of Optometry"},
	{"career": "Dentist", "course": "Doctor of Dental Medicine"},
	{"career": "Anthropologist", "course": "BA Anthropology"},
	{"career": "Sociologist", "course": "BA Sociology"},
	{"career": "Historian", "course": "BA History"},
	{"career": "Museum Curator", "course": "BA Art Studies"},
	{"career": "Diplomat", "course": "BA International Studies"},
	{"career": "English Instructor", "course": "BA English Language Studies"},
	{"career": "Philosophy Professor", "course": "BA Philosophy"},
	{"career": "Technical Writer", "course": "BA English"},
	{"career": "Biochemist", "course": "BS Biochemistry"},
	{"career": "Meteorologist", "course": "BS Meteorology"},
	{"career": "Astrophysicist", "course": "BS Applied Physics"},
	{"career": "Materials Engineer", "course": "BS Materials Engineering"},
	{"career": "Sanitary Engineer", "course": "BS Sanitary Engineering"},
	{"career": "Electronics Engineer", "course": "BS Electronics Engineering"},
	{"career": "Entrepreneur", "course": "BS Entrepreneurship"},
	{"career": "Digital Marketer", "course": "BSBA Marketing Management"},
	{"career": "E-Commerce Manager", "course": "BS Information Systems"},
	{"career": "Office Administrator", "course": "BS Office Administration"},
	{"career": "Event Coordinator", "course": "BS Tourism Management"},
	{"career": "Tour Guide", "course": "BS Tourism"},
	{"career": "Pastry Chef", "course": "BS Hospitality Management"},
	{"career": "Agribusiness Manager", "course": "BS Agribusiness"},
	{"career": "Forester", "course": "BS Forestry"},
	{"career": "Fisheries Technologist", "course": "BS Fisheries"},
	{"career": "Environmental Officer", "course": "BS Environmental Management"},
	{"career": "Database Manager", "course": "BS Information Technology"},
	{"career": "Cloud Architect", "course": "BS Computer Science"},
	{"career": "AI Researcher", "course": "BS Applied Mathematics"},
	{"career": "Quality Analyst", "course": "BS Industrial Engineering"},
	{"career": "Telecom Engineer", "course": "BS Electronics Engineering"},
	{"career": "Paralegal", "course": "BS Legal Management"},
	{"career": "Public Servant", "course": "BS Public Administration"},
	{"career": "Logistics Officer", "course": "BS Customs Administration"},
	{"career": "Sports Coach", "course": "BS Sports Science"},
	{"career": "Advertising Director", "course": "BFA Advertising Arts"},
]

# User-defined plotting targets for each career option.
CAREER_PLOTTING_OVERRIDES = {
	"Civil Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Marketing Manager": {"best_subject": "ENGLISH", "shs_strand": "ABM", "holland_code": "EAS"},
	"Software Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "IRC"},
	"Registered Nurse": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "SIR"},
	"CPA Accountant": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "CEI"},
	"Psychometrician": {"best_subject": "SCIENCE", "shs_strand": "HUMSS", "holland_code": "ISA"},
	"Data Scientist": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "ICR"},
	"Architect": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "AIR"},
	"Licensed Pharmacist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "ICS"},
	"Graphic Designer": {"best_subject": "SCIENCE", "shs_strand": "ICT", "holland_code": "ARS"},
	"Mechanical Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Lawyer / Attorney": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ESI"},
	"IT Specialist": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "RIC"},
	"Medical Technologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRC"},
	"Financial Analyst": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "IEC"},
	"News Journalist": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "AES"},
	"Electrical Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Executive Chef": {"best_subject": "SCIENCE", "shs_strand": "HE", "holland_code": "RAE"},
	"Veterinarian": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRS"},
	"HR Manager": {"best_subject": "ENGLISH", "shs_strand": "ABM", "holland_code": "ESC"},
	"Aircraft Mechanic": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RCI"},
	"Social Worker": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SIE"},
	"Cybersecurity Analyst": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "IRC"},
	"Microbiologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRS"},
	"Hotel Manager": {"best_subject": "ENGLISH", "shs_strand": "HE", "holland_code": "ESC"},
	"Physical Therapist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "SIR"},
	"Geodetic Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Librarian": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "CSE"},
	"Environmental Planner": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IEA"},
	"Economist": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "IAS"},
	"Chemical Engineer": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRC"},
	"Criminologist": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "RES"},
	"Interior Designer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "ARE"},
	"Radiologic Technologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIC"},
	"Customs Broker": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "CEI"},
	"PR Specialist": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "EAS"},
	"Computer Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Nutritionist-Dietitian": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "ISE"},
	"Flight Attendant": {"best_subject": "ENGLISH", "shs_strand": "HE", "holland_code": "ESR"},
	"Real Estate Broker": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ECS"},
	"Industrial Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "IEC"},
	"Agriculturist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIS"},
	"Marine Biologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRS"},
	"Systems Administrator": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "RIC"},
	"Occupational Therapist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "SIR"},
	"Game Developer": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "AIR"},
	"Marine Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Merchant Marine Officer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "REC"},
	"Geologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRS"},
	"Actuary": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "ICR"},
	"Software Tester": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "ICR"},
	"Preschool Teacher": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SAE"},
	"SPED Teacher": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SIR"},
	"High School Teacher": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SIR"},
	"Mining Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Petroleum Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Forensic Investigator": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRC"},
	"Bank Manager": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ECS"},
	"Operations Manager": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ECS"},
	"UI/UX Designer": {"best_subject": "SCIENCE", "shs_strand": "ICT", "holland_code": "AIR"},
	"App Developer": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "IRC"},
	"Radio/TV Broadcaster": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "AES"},
	"Fashion Designer": {"best_subject": "SCIENCE", "shs_strand": "HE", "holland_code": "ARS"},
	"Optometrist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "ISR"},
	"Dentist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIC"},
	"Anthropologist": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ISA"},
	"Sociologist": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ISA"},
	"Historian": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ISA"},
	"Museum Curator": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "AEC"},
	"Diplomat": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ESI"},
	"English Instructor": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SAE"},
	"Philosophy Professor": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "ISA"},
	"Technical Writer": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "AIC"},
	"Biochemist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRC"},
	"Meteorologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "IRC"},
	"Astrophysicist": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "IRC"},
	"Materials Engineer": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIC"},
	"Sanitary Engineer": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIC"},
	"Electronics Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Entrepreneur": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ESR"},
	"Digital Marketer": {"best_subject": "ENGLISH", "shs_strand": "ABM", "holland_code": "EAS"},
	"E-Commerce Manager": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ECS"},
	"Office Administrator": {"best_subject": "ENGLISH", "shs_strand": "ABM", "holland_code": "CES"},
	"Event Coordinator": {"best_subject": "ENGLISH", "shs_strand": "HE", "holland_code": "ECS"},
	"Tour Guide": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SER"},
	"Pastry Chef": {"best_subject": "SCIENCE", "shs_strand": "HE", "holland_code": "RAC"},
	"Agribusiness Manager": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "ERS"},
	"Forester": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIS"},
	"Fisheries Technologist": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "RIS"},
	"Environmental Officer": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "ISR"},
	"Database Manager": {"best_subject": "MATH", "shs_strand": "ICT", "holland_code": "CIR"},
	"Cloud Architect": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "IRC"},
	"AI Researcher": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "IRC"},
	"Quality Analyst": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "ICR"},
	"Telecom Engineer": {"best_subject": "MATH", "shs_strand": "STEM", "holland_code": "RIC"},
	"Paralegal": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "CEI"},
	"Public Servant": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "SEC"},
	"Logistics Officer": {"best_subject": "MATH", "shs_strand": "ABM", "holland_code": "CRE"},
	"Sports Coach": {"best_subject": "SCIENCE", "shs_strand": "STEM", "holland_code": "SRE"},
	"Advertising Director": {"best_subject": "ENGLISH", "shs_strand": "HUMSS", "holland_code": "AES"},
}

SUBJECT_NORMALIZATION = {
	"MATH": "Math",
	"ENGLISH": "English",
	"SCIENCE": "Science",
}

HOLLAND_POSITION_WEIGHTS = (3, 2, 1)
RIASEC_LETTERS = "RIASEC"
ALL_HOLLAND_CODES = ["".join(code) for code in permutations(RIASEC_LETTERS, 3)]
HOLLAND_CODE_INDEX = {code: index for index, code in enumerate(ALL_HOLLAND_CODES)}

STRAND_KEYWORDS = {
	"STEM": {
		"engineer",
		"doctor",
		"nurse",
		"pharmac",
		"therap",
		"scient",
		"biology",
		"chem",
		"physics",
		"geolog",
		"meteor",
		"veter",
		"agri",
		"forensic",
		"marine",
	},
	"ABM": {
		"manager",
		"marketing",
		"account",
		"finance",
		"econom",
		"entrepreneur",
		"bank",
		"business",
		"operations",
		"real estate",
		"office admin",
		"logistics",
		"customs",
		"broker",
	},
	"HUMSS": {
		"lawyer",
		"attorney",
		"journal",
		"social",
		"teacher",
		"instructor",
		"professor",
		"writer",
		"communication",
		"broadcast",
		"anthrop",
		"sociolog",
		"history",
		"philosophy",
		"diplomat",
		"public admin",
		"paralegal",
		"criminolog",
	},
	"ICT": {
		"software",
		"computer",
		"information system",
		"information technology",
		"cyber",
		"systems",
		"database",
		"cloud",
		"app",
		"ui/ux",
		"game",
		"ai",
		"data",
		"telecom",
	},
	"HE": {
		"chef",
		"culinary",
		"hospitality",
		"tourism",
		"tour guide",
		"flight attendant",
		"hotel",
		"event",
		"pastry",
	},
}

STRAND_DEFAULT_SUBJECTS = {
	"STEM": {"Math", "Science"},
	"ABM": {"Math", "English"},
	"HUMSS": {"English", "Science"},
	"ICT": {"Math", "English"},
	"HE": {"English", "Science"},
}

RIASEC_BASE_PROFILES = {
	"STEM": {"R": 3, "I": 3, "A": 1, "S": 1, "E": 1, "C": 2},
	"ABM": {"R": 1, "I": 1, "A": 1, "S": 2, "E": 3, "C": 3},
	"HUMSS": {"R": 1, "I": 2, "A": 2, "S": 3, "E": 2, "C": 1},
	"ICT": {"R": 2, "I": 3, "A": 1, "S": 1, "E": 1, "C": 2},
	"HE": {"R": 1, "I": 1, "A": 2, "S": 3, "E": 2, "C": 2},
}

SCCT_BASE_IDEALS = {
	"STEM": {"se": 4, "oe": 4, "b": 2},
	"ABM": {"se": 3, "oe": 4, "b": 3},
	"HUMSS": {"se": 4, "oe": 4, "b": 3},
	"ICT": {"se": 4, "oe": 4, "b": 2},
	"HE": {"se": 3, "oe": 4, "b": 3},
}


def stable_seed(text: str) -> int:
	return sum((index + 1) * ord(char) for index, char in enumerate(text))


def clamp(value: int, minimum: int, maximum: int) -> int:
	return max(minimum, min(value, maximum))


def normalize_best_subject(subject: str) -> str:
	normalized = subject.strip().upper()
	if normalized not in SUBJECT_NORMALIZATION:
		raise ValueError(f"Unsupported best_subject override: {subject}")
	return SUBJECT_NORMALIZATION[normalized]


def build_override_subject_profile(best_subject: str) -> dict[str, float]:
	return {
		subject: (1.0 if subject == best_subject else 0.25)
		for subject in ("Math", "English", "Science")
	}


def build_override_strand_affinity(shs_strand: str) -> dict[str, float]:
	return {
		strand: (1.0 if strand == shs_strand else 0.2)
		for strand in STRAND_KEYWORDS
	}


def build_override_riasec_profile(holland_code: str) -> dict[str, int]:
	profile = {letter: 1 for letter in RIASEC_LETTERS}
	for boost, letter in zip((5, 4, 3), holland_code):
		profile[letter] = min(6, profile[letter] + boost)
	return profile


def build_override_preferred_holland_codes(primary_holland_code: str, seed: int) -> set[str]:
	index = seed % len(ALL_HOLLAND_CODES)
	alt_code_a = ALL_HOLLAND_CODES[index]
	alt_code_b = ALL_HOLLAND_CODES[(index + 17) % len(ALL_HOLLAND_CODES)]
	alt_code_c = ALL_HOLLAND_CODES[(index + 53) % len(ALL_HOLLAND_CODES)]
	return {primary_holland_code, alt_code_a, alt_code_b, alt_code_c}


def validate_plotting_overrides() -> None:
	careers = {option["career"] for option in CAREER_OPTIONS}
	override_careers = set(CAREER_PLOTTING_OVERRIDES)

	missing = sorted(careers - override_careers)
	extra = sorted(override_careers - careers)
	if missing or extra:
		messages = []
		if missing:
			messages.append(f"Missing career overrides: {', '.join(missing)}")
		if extra:
			messages.append(f"Unknown career overrides: {', '.join(extra)}")
		raise ValueError(" | ".join(messages))

	for career, override in CAREER_PLOTTING_OVERRIDES.items():
		normalize_best_subject(override["best_subject"])

		shs_strand = override["shs_strand"]
		if shs_strand not in STRAND_KEYWORDS:
			raise ValueError(f"Unsupported shs_strand override for {career}: {shs_strand}")

		holland_code = override["holland_code"]
		if holland_code not in HOLLAND_CODE_INDEX:
			raise ValueError(f"Unsupported holland_code override for {career}: {holland_code}")


def contains_keyword(text: str, keyword: str) -> bool:
	# Use strict token matching for short keywords (e.g., HR) to avoid accidental matches.
	if len(keyword) <= 3 and " " not in keyword:
		pattern = rf"\b{re.escape(keyword)}\b"
		return re.search(pattern, text) is not None
	return keyword in text


def keyword_hits(text: str, keywords: set[str]) -> int:
	return sum(1 for keyword in keywords if contains_keyword(text, keyword))


def infer_strand_affinity(career: str, course: str) -> dict[str, float]:
	text = f"{career} {course}".lower()
	strand_scores = {
		strand: keyword_hits(text, keywords)
		for strand, keywords in STRAND_KEYWORDS.items()
	}

	if max(strand_scores.values()) == 0:
		if "ba " in text or "bachelor of" in text:
			strand_scores["HUMSS"] = 2
		if "bsba" in text or "business" in text:
			strand_scores["ABM"] = 2
		if "it" in text or "computer" in text:
			strand_scores["ICT"] = 2
		if max(strand_scores.values()) == 0:
			strand_scores["STEM"] = 2

	max_score = max(strand_scores.values())
	return {
		strand: strand_scores[strand] / max_score if max_score else 0.0
		for strand in STRAND_KEYWORDS
	}


def infer_primary_strand(strand_affinity: dict[str, float]) -> str:
	priority = {"HE": 5, "ICT": 4, "STEM": 3, "ABM": 2, "HUMSS": 1}
	return max(
		strand_affinity,
		key=lambda strand: (strand_affinity[strand], priority[strand]),
	)


def infer_subject_profile(career: str, course: str, strand: str) -> dict[str, float]:
	text = f"{career} {course}".lower()
	subject_scores = {"Math": 0.0, "Science": 0.0, "English": 0.0}

	math_keywords = {
		"engineer",
		"account",
		"finance",
		"econom",
		"analyst",
		"actuary",
		"statistics",
		"mathematics",
		"data",
		"computer",
		"cyber",
		"systems",
		"logistics",
	}
	science_keywords = {
		"nurse",
		"medical",
		"pharmac",
		"biology",
		"chemist",
		"veter",
		"therapy",
		"science",
		"forensic",
		"geology",
		"meteor",
		"agri",
		"fisher",
	}
	english_keywords = {
		"lawyer",
		"attorney",
		"journal",
		"teacher",
		"instructor",
		"writer",
		"communication",
		"broadcaster",
		"diplomat",
		"manager",
		"director",
		"social",
		"designer",
		"tour",
	}

	subject_scores["Math"] += keyword_hits(text, math_keywords)
	subject_scores["Science"] += keyword_hits(text, science_keywords)
	subject_scores["English"] += keyword_hits(text, english_keywords)

	for subject in STRAND_DEFAULT_SUBJECTS[strand]:
		subject_scores[subject] += 1.0

	max_score = max(subject_scores.values())
	if max_score == 0:
		for subject in STRAND_DEFAULT_SUBJECTS[strand]:
			subject_scores[subject] = 1.0
		max_score = 1.0

	return {
		subject: subject_scores[subject] / max_score
		for subject in subject_scores
	}


def infer_riasec_profile(career: str, course: str, strand: str) -> dict[str, int]:
	text = f"{career} {course}".lower()
	profile = dict(RIASEC_BASE_PROFILES[strand])

	if keyword_hits(text, {"designer", "arts", "fashion", "multimedia", "museum", "advertising", "ui/ux"}):
		profile["A"] += 2
	if keyword_hits(text, {"social", "teacher", "coach", "hr", "communication", "public", "lawyer", "nurse"}):
		profile["S"] += 2
	if keyword_hits(text, {"manager", "director", "entrepreneur", "marketing", "bank", "broker", "finance"}):
		profile["E"] += 2
		profile["C"] += 1
	if keyword_hits(text, {"scient", "analyst", "research", "biolog", "chemist", "forensic", "data"}):
		profile["I"] += 2
	if keyword_hits(text, {"engineer", "mechanic", "architect", "marine", "aircraft", "industrial", "telecom"}):
		profile["R"] += 2
	if keyword_hits(text, {"account", "administrator", "librarian", "office", "customs", "quality"}):
		profile["C"] += 2

	for letter, value in profile.items():
		profile[letter] = max(1, min(value, 6))

	return profile


def infer_preferred_holland_codes(
	riasec_profile: dict[str, int],
	seed: int,
) -> tuple[str, set[str]]:
	ordered_letters = sorted(
		riasec_profile,
		key=lambda letter: (riasec_profile[letter], letter),
		reverse=True,
	)
	primary = "".join(ordered_letters[:3])

	index = seed % len(ALL_HOLLAND_CODES)
	alt_code_a = ALL_HOLLAND_CODES[index]
	alt_code_b = ALL_HOLLAND_CODES[(index + 17) % len(ALL_HOLLAND_CODES)]
	alt_code_c = ALL_HOLLAND_CODES[(index + 53) % len(ALL_HOLLAND_CODES)]

	return primary, {primary, alt_code_a, alt_code_b, alt_code_c}


def compute_signature_holland_fit(seed: int, holland_code: str) -> float:
	index = HOLLAND_CODE_INDEX[holland_code]
	return ((seed * 37 + index * 19) % 997) / 996.0


def infer_scct_ideal(career: str, course: str, strand: str) -> dict[str, int]:
	text = f"{career} {course}".lower()
	ideal = dict(SCCT_BASE_IDEALS[strand])
	seed = stable_seed(text)

	licensed_keywords = {
		"engineer",
		"lawyer",
		"attorney",
		"nurse",
		"pharmac",
		"doctor",
		"dentist",
		"optometrist",
		"therap",
		"veter",
		"architect",
		"account",
		"teacher",
		"technologist",
	}
	if keyword_hits(text, licensed_keywords):
		ideal["se"] = min(5, ideal["se"] + 1)
		ideal["oe"] = min(5, ideal["oe"] + 1)
		ideal["b"] = max(1, ideal["b"] - 1)

	if keyword_hits(text, {"manager", "director", "officer"}):
		ideal["oe"] = min(5, ideal["oe"] + 1)

	# Career-specific SCCT diversity avoids over-clustering to a few options.
	ideal["se"] = clamp(ideal["se"] + ((seed % 3) - 1), 1, 5)
	ideal["oe"] = clamp(ideal["oe"] + (((seed // 3) % 3) - 1), 1, 5)
	ideal["b"] = clamp(ideal["b"] + (((seed // 9) % 3) - 1), 1, 5)

	return ideal


def build_all_career_options() -> list[dict]:
	validate_plotting_overrides()
	options = []
	for option in CAREER_OPTIONS:
		career = option["career"]
		course = option["course"]
		text = f"{career} {course}".lower()
		seed = stable_seed(text)

		override = CAREER_PLOTTING_OVERRIDES.get(career)
		if override:
			strand = override["shs_strand"]
			best_subject = normalize_best_subject(override["best_subject"])
			primary_holland_code = override["holland_code"]
			strand_affinity = build_override_strand_affinity(strand)
			subject_profile = build_override_subject_profile(best_subject)
			riasec_profile = build_override_riasec_profile(primary_holland_code)
			preferred_holland_codes = build_override_preferred_holland_codes(
				primary_holland_code,
				seed,
			)
		else:
			strand_affinity = infer_strand_affinity(career, course)
			strand = infer_primary_strand(strand_affinity)
			subject_profile = infer_subject_profile(career, course, strand)
			best_subject = max(subject_profile, key=subject_profile.get)
			riasec_profile = infer_riasec_profile(career, course, strand)
			primary_holland_code, preferred_holland_codes = infer_preferred_holland_codes(
				riasec_profile,
				seed,
			)

		options.append(
			{
				"career": career,
				"course": course,
				"seed": seed,
				"strand": strand,
				"strand_affinity": strand_affinity,
				"best_subject_hint": best_subject,
				"subject_profile": subject_profile,
				"riasec_profile": riasec_profile,
				"primary_holland_code": primary_holland_code,
				"preferred_holland_codes": preferred_holland_codes,
				"scct_ideal": infer_scct_ideal(career, course, strand),
			}
		)
	return options


ALL_CAREER_OPTIONS = build_all_career_options()
FEATURE_WEIGHTS = {
	"best_subject": 10,
	"shs_strand": 10,
	"holland_code": 50,
	"scct_se": 10,
	"scct_oe": 10,
	"scct_b": 10,
}


def compute_holland_score(
	holland_code: str,
	riasec_profile: dict[str, int],
	primary_holland_code: str,
	preferred_holland_codes: set[str],
	seed: int,
	holland_position_weights: tuple[int, int, int] = HOLLAND_POSITION_WEIGHTS,
) -> float:
	"""Return normalized Holland fit between 0.0 and 1.0 using RIASEC ranking."""
	raw_score = 0
	for weight, letter in zip(holland_position_weights, holland_code):
		raw_score += weight * riasec_profile.get(letter, 0)

	max_profile = max(riasec_profile.values()) if riasec_profile else 1
	max_raw = sum(weight * max_profile for weight in holland_position_weights)
	base_fit = raw_score / max_raw if max_raw else 0.0

	if holland_code == primary_holland_code:
		specialization_fit = 1.0
	elif holland_code in preferred_holland_codes:
		specialization_fit = 0.92
	elif holland_code[:2] == primary_holland_code[:2]:
		specialization_fit = 0.82
	elif holland_code[0] == primary_holland_code[0]:
		specialization_fit = 0.72
	elif holland_code[1] == primary_holland_code[1]:
		specialization_fit = 0.58
	else:
		specialization_fit = 0.28

	signature_fit = compute_signature_holland_fit(seed, holland_code)
	return 0.55 * base_fit + 0.30 * specialization_fit + 0.15 * signature_fit


def compute_scct_score(actual: int, ideal: int) -> float:
	"""Return normalized SCCT fit between 0.0 and 1.0 for one SCCT dimension."""
	return max(0.0, 1.0 - (abs(actual - ideal) / 4.0))


def compute_scct_component_score(
	scct_se: int,
	scct_oe: int,
	scct_b: int,
	ideal: dict[str, int],
) -> float:
	"""Compute weighted SCCT score using exact 10/10/10 component percentages."""
	se_fit = compute_scct_score(scct_se, ideal["se"])
	oe_fit = compute_scct_score(scct_oe, ideal["oe"])
	b_fit = compute_scct_score(scct_b, ideal["b"])

	return (
		FEATURE_WEIGHTS["scct_se"] * se_fit
		+ FEATURE_WEIGHTS["scct_oe"] * oe_fit
		+ FEATURE_WEIGHTS["scct_b"] * b_fit
	)


def career_total_score(
	option: dict,
	best_subject: str,
	shs_strand: str,
	holland_code: str,
	scct_se: int,
	scct_oe: int,
	scct_b: int,
) -> float:
	"""Compute exact weighted score: 10% subject, 10% strand, 50% Holland, 30% SCCT."""
	subject_fit = option["subject_profile"][best_subject]
	strand_fit = option["strand_affinity"][shs_strand]
	holland_fit = compute_holland_score(
		holland_code,
		option["riasec_profile"],
		option["primary_holland_code"],
		option["preferred_holland_codes"],
		option["seed"],
	)
	scct_score = compute_scct_component_score(scct_se, scct_oe, scct_b, option["scct_ideal"])

	return (
		FEATURE_WEIGHTS["best_subject"] * subject_fit
		+ FEATURE_WEIGHTS["shs_strand"] * strand_fit
		+ FEATURE_WEIGHTS["holland_code"] * holland_fit
		+ scct_score
	)


def map_career_and_course(
	best_subject: str,
	shs_strand: str,
	holland_code: str,
	scct_se: int,
	scct_oe: int,
	scct_b: int,
) -> tuple[str, str]:
	"""Select best career and course using global weighted counselor scoring."""
	options = ALL_CAREER_OPTIONS
	holland_index = HOLLAND_CODE_INDEX[holland_code]

	def tie_break(option: dict) -> float:
		value = (
			option["seed"]
			+ holland_index * 29
			+ scct_se * 11
			+ scct_oe * 7
			+ scct_b * 5
		)
		return (value % 1009) / 1008.0

	best_option = max(
		options,
		key=lambda option: (
			career_total_score(
				option,
				best_subject,
				shs_strand,
				holland_code,
				scct_se,
				scct_oe,
				scct_b,
			),
			tie_break(option),
		),
	)

	return best_option["career"], best_option["course"]


def apply_plotting_anchor_rows(df: pd.DataFrame) -> pd.DataFrame:
	"""Guarantee at least one exact row per career for requested plotting fields."""
	reserved_indices: set[int] = set()

	for option in ALL_CAREER_OPTIONS:
		best_subject = option["best_subject_hint"]
		shs_strand = option["strand"]
		holland_code = option["primary_holland_code"]
		ideal = option["scct_ideal"]

		candidates = df[
			(df["best_subject"] == best_subject)
			& (df["shs_strand"] == shs_strand)
			& (df["holland_code"] == holland_code)
		].copy()
		if candidates.empty:
			continue

		candidates["distance"] = (
			(candidates["scct_se"] - ideal["se"]).abs()
			+ (candidates["scct_oe"] - ideal["oe"]).abs()
			+ (candidates["scct_b"] - ideal["b"]).abs()
		)
		candidates = candidates.sort_values(["distance", "suggestion_id"])

		chosen_index = None
		for index in candidates.index.tolist():
			if index not in reserved_indices:
				chosen_index = int(index)
				break

		if chosen_index is None:
			chosen_index = int(candidates.index[0])

		reserved_indices.add(chosen_index)
		df.at[chosen_index, "best_career"] = option["career"]
		df.at[chosen_index, "best_course"] = option["course"]

	return df


def generate_dataset(
	output_file: str = "career_suggestion.csv",
) -> pd.DataFrame:
	best_subjects = ["Math", "English", "Science"]
	shs_strands = ["STEM", "ABM", "HUMSS", "ICT", "HE"]
	holland_codes = ["".join(code) for code in permutations("RIASEC", 3)]
	scct_values = [1, 2, 3, 4, 5]

	rows = []
	suggestion_id = 1

	for best_subject, shs_strand, holland_code, scct_se, scct_oe, scct_b in product(
		best_subjects,
		shs_strands,
		holland_codes,
		scct_values,
		scct_values,
		scct_values,
	):
		best_career, best_course = map_career_and_course(
			best_subject,
			shs_strand,
			holland_code,
			scct_se,
			scct_oe,
			scct_b,
		)

		rows.append(
			{
				"suggestion_id": suggestion_id,
				"best_subject": best_subject,
				"shs_strand": shs_strand,
				"holland_code": holland_code,
				"scct_se": scct_se,
				"scct_oe": scct_oe,
				"scct_b": scct_b,
				"best_career": best_career,
				"best_course": best_course,
			}
		)
		suggestion_id += 1

	df = pd.DataFrame(
		rows,
		columns=[
			"suggestion_id",
			"best_subject",
			"shs_strand",
			"holland_code",
			"scct_se",
			"scct_oe",
			"scct_b",
			"best_career",
			"best_course",
		],
	)

	df = apply_plotting_anchor_rows(df)

	df.to_csv(output_file, index=False)
	return df


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate career suggestions dataset.")
	parser.add_argument(
		"--output",
		default="career_suggestion.csv",
		help="Output CSV filename.",
	)
	args = parser.parse_args()

	dataset = generate_dataset(args.output)
	print(
		f"Generated {args.output} with {len(dataset)} rows using weighted 10/10/50/10/10/10 scoring."
	)
