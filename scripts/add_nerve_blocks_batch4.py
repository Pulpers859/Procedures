import json

PROCEDURES_FILE = r"C:\Dev\Procedures\Procedures\Resources\procedures.json"

new_blocks = [
  {
    "id": "block_supraorbital",
    "title": "Supraorbital Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "forehead block",
      "supraorbital",
      "supratrochlear"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: Supraorbital and supratrochlear nerves as they exit the supraorbital rim.",
      "Provides anesthesia to the forehead and anterior scalp.",
      "Landmark-guided injection along the superior orbital rim."
    ],
    "indications": [
      "Forehead lacerations",
      "Anterior scalp lacerations",
      "Abscess drainage on the forehead"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The supraorbital notch/foramen is located on the superior orbital rim, typically in line with the patient's pupil when looking straight ahead.",
      "The supratrochlear nerve exits slightly medial to this."
    ],
    "equipment": [
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (3-5 mL of 1% or 2% lidocaine with epinephrine)"
    ],
    "positioning": [
      "Patient supine or seated."
    ],
    "steps": [
      "Palpate the superior orbital rim to find the supraorbital notch (in line with the pupil).",
      "Cleanse the skin.",
      "Insert the needle subcutaneously just above the eyebrow, aiming medially over the notch.",
      "Aspirate, then inject 1-2 mL over the notch.",
      "To block the supratrochlear nerve, advance the needle slightly further medially towards the bridge of the nose and inject another 1-2 mL."
    ],
    "ultrasound": [
      "Not typically required. Can be used to identify the notch (a break in the hyperechoic bony line of the orbital rim) if landmarks are obscured by swelling."
    ],
    "confirmation": [
      "Numbness of the forehead and anterior scalp extending back to the vertex."
    ],
    "troubleshooting": [
      "If the block fails, simply inject a continuous subcutaneous band of anesthetic along the entire eyebrow (a 'field block')."
    ],
    "complications": [
      "Intravascular injection",
      "Hematoma (black eye if fluid tracks down into the eyelid)"
    ],
    "aftercare": [
      "Routine wound care. Warn the patient about potential eyelid swelling if volume was large."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Adding epinephrine helps reduce bleeding for forehead lacerations and prolongs the block.",
      "Always apply pressure to the upper eyelid below the injection site to prevent the anesthetic from tracking downward and causing a swollen eyelid."
    ]
  },
  {
    "id": "block_infraorbital",
    "title": "Infraorbital Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "cheek block",
      "upper lip block",
      "infraorbital"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: Infraorbital nerve as it exits the infraorbital foramen on the maxilla.",
      "Provides anesthesia to the lower eyelid, cheek, lateral nose, and upper lip.",
      "Can be performed via an intraoral (preferred) or extraoral approach."
    ],
    "indications": [
      "Upper lip lacerations (especially those crossing the vermilion border)",
      "Cheek lacerations",
      "Nasal lacerations"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The infraorbital foramen is located on the maxilla, roughly 1 cm below the inferior orbital rim, directly below the pupil.",
      "It is in line with the supraorbital notch and the mental foramen."
    ],
    "equipment": [
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (2-3 mL of 1% or 2% lidocaine with epinephrine)",
      "Topical anesthetic (e.g., benzocaine gel) for intraoral approach"
    ],
    "positioning": [
      "Patient supine or seated."
    ],
    "steps": [
      "**Intraoral Approach (Preferred):**",
      "Palpate the infraorbital foramen extraorally with your non-dominant index finger.",
      "Apply topical anesthetic to the buccal mucosa above the maxillary canine/first premolar.",
      "Retract the upper lip.",
      "Insert the needle into the mucobuccal fold above the canine/first premolar, directing it superiorly toward your palpating finger.",
      "Stop before hitting the bone or entering the foramen.",
      "Aspirate, then inject 2-3 mL of anesthetic."
    ],
    "ultrasound": [
      "Can be used extraorally to identify the foramen (a break in the hyperechoic maxillary bone) and guide an extraoral injection."
    ],
    "confirmation": [
      "Numbness of the upper lip, cheek, and side of the nose."
    ],
    "troubleshooting": [
      "Do NOT enter the foramen. Injecting directly into the foramen can cause nerve injury or severe pressure necrosis. Injecting in the tissue *near* the foramen is sufficient."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury (if injected into the foramen)"
    ],
    "aftercare": [
      "Routine wound care."
    ],
    "documentation": [
      "Pre/post exam, approach used (intraoral vs extraoral), volume and type of anesthetic."
    ],
    "seniorPearls": [
      "The intraoral approach is much less painful for the patient than going through the facial skin.",
      "This block is essential for perfectly aligning the vermilion border of the upper lip without distorting the tissue with local infiltration."
    ]
  },
  {
    "id": "block_mental",
    "title": "Mental Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "lower lip block",
      "chin block",
      "mental"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: Mental nerve as it exits the mental foramen on the mandible.",
      "Provides anesthesia to the lower lip and chin.",
      "Intraoral approach is preferred."
    ],
    "indications": [
      "Lower lip lacerations (especially crossing the vermilion border)",
      "Chin lacerations"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The mental foramen is located on the anterior mandible, typically below the first or second mandibular premolar.",
      "It is in line with the pupil, supraorbital notch, and infraorbital foramen."
    ],
    "equipment": [
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (2-3 mL of 1% or 2% lidocaine with epinephrine)",
      "Topical anesthetic (e.g., benzocaine gel) for intraoral approach"
    ],
    "positioning": [
      "Patient supine or seated."
    ],
    "steps": [
      "**Intraoral Approach:**",
      "Retract the lower lip to expose the mucobuccal fold.",
      "Apply topical anesthetic to the mucosa below the first/second premolar.",
      "Palpate the mental foramen through the mucosa.",
      "Insert the needle into the mucobuccal fold directed inferiorly toward the foramen.",
      "Stop before hitting the bone or entering the foramen.",
      "Aspirate, then inject 2-3 mL of anesthetic."
    ],
    "ultrasound": [
      "Can be used extraorally to identify the foramen on the mandible if landmarks are unclear."
    ],
    "confirmation": [
      "Numbness of the lower lip and chin on the ipsilateral side."
    ],
    "troubleshooting": [
      "Like the infraorbital block, do NOT inject into the foramen itself to avoid nerve injury."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury"
    ],
    "aftercare": [
      "Routine wound care."
    ],
    "documentation": [
      "Pre/post exam, approach used, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "This is the fastest, easiest, and least painful way to repair a complex lower lip laceration."
    ]
  },
  {
    "id": "block_inferior_alveolar",
    "title": "Inferior Alveolar Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "dental block",
      "mandibular block",
      "ianb"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: Inferior alveolar nerve before it enters the mandibular foramen on the medial aspect of the mandibular ramus.",
      "Provides profound anesthesia to all mandibular teeth to the midline, the lower lip, and the chin.",
      "The 'gold standard' for lower jaw dental pain in the ED."
    ],
    "indications": [
      "Severe dental pain of the lower teeth (caries, abscess, fracture)",
      "Mandibular fractures (for pain control)",
      "Dry socket (alveolar osteitis)"
    ],
    "contraindications": [
      "Infection in the retromolar/pterygomandibular space",
      "Allergy to local anesthetic",
      "Coagulopathy"
    ],
    "anatomy": [
      "The nerve enters the mandibular foramen on the medial surface of the ramus.",
      "The lingual nerve lies just anterior/medial to it.",
      "Landmarks: Coronoid notch (anterior border of ramus) and pterygomandibular raphe."
    ],
    "equipment": [
      "25G or 27G needle (long, 1.5 inch minimum)",
      "Local anesthetic (2-3 mL of 0.5% bupivacaine for long duration, or lidocaine/articaine)",
      "Topical anesthetic"
    ],
    "positioning": [
      "Patient seated, head resting firmly against the chair/bed, mouth opened as wide as possible."
    ],
    "steps": [
      "Apply topical anesthetic to the mucosa posterior to the last molar.",
      "Palpate the greatest concavity on the anterior border of the mandibular ramus (coronoid notch) with your non-dominant thumb.",
      "Visualize the pterygomandibular raphe (a vertical fold of tissue medial to the ramus).",
      "Approach with the syringe barrel resting over the premolars of the *opposite* side of the mouth.",
      "Insert the needle at the midpoint between your thumb and the raphe, about 1 cm above the occlusal plane of the lower molars.",
      "Advance until you contact bone (usually ~20-25 mm).",
      "Withdraw 1-2 mm, aspirate carefully (high vascularity area), and inject 1.5-2 mL.",
      "As you withdraw the needle halfway, inject the remaining 0.5 mL to block the lingual nerve."
    ],
    "ultrasound": [
      "Not routinely used for this block, though intraoral/extraoral US-guided techniques exist in the literature."
    ],
    "confirmation": [
      "Profound numbness of the lower teeth, lower lip, and ipsilateral anterior 2/3 of the tongue (lingual nerve)."
    ],
    "troubleshooting": [
      "If you do not hit bone, you are too far posterior (risk of injecting into the parotid gland and paralyzing the facial nerve). Withdraw and redirect more laterally.",
      "If you hit bone immediately, you are too far anterior. Withdraw and redirect more medially."
    ],
    "complications": [
      "Transient facial nerve paralysis (if injected into parotid gland)",
      "Intravascular injection",
      "Trismus (jaw stiffness) post-injection",
      "Needle breakage (rare, do not bend the needle)"
    ],
    "aftercare": [
      "Warn the patient not to chew on their numb lip or tongue.",
      "Prescribe appropriate dental follow-up."
    ],
    "documentation": [
      "Pre/post exam, volume and type of anesthetic, confirmation of bone contact prior to injection."
    ],
    "seniorPearls": [
      "Using long-acting bupivacaine gives the patient 12-24 hours of profound pain relief, allowing them to sleep and find a dentist the next day.",
      "Always contact bone! If you don't feel the hard stop, do not inject."
    ]
  },
  {
    "id": "block_superior_alveolar",
    "title": "Superior Alveolar Nerve Block (Supraperiosteal)",
    "icon": "lungs",
    "searchTerms": [
      "maxillary block",
      "upper dental",
      "supraperiosteal"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: The small nerve branches entering the apex of the maxillary tooth roots.",
      "Unlike the dense mandible, the maxillary bone is porous, allowing anesthetic to diffuse directly through the bone to the tooth root (Supraperiosteal infiltration).",
      "Provides anesthesia to individual upper teeth."
    ],
    "indications": [
      "Maxillary dental pain (caries, abscess, fracture)",
      "Procedures on individual upper teeth"
    ],
    "contraindications": [
      "Injection directly into an infected area or abscess",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The roots of the maxillary teeth sit just above the mucobuccal fold.",
      "The porous maxilla allows fluid injected at the mucobuccal fold to penetrate to the nerve."
    ],
    "equipment": [
      "25G or 27G needle (short, 1 inch is fine)",
      "Local anesthetic (1-2 mL of 0.5% bupivacaine or lidocaine)",
      "Topical anesthetic"
    ],
    "positioning": [
      "Patient seated, head resting firmly."
    ],
    "steps": [
      "Identify the specific tooth causing pain.",
      "Apply topical anesthetic to the mucobuccal fold directly above that tooth.",
      "Retract the upper lip/cheek.",
      "Insert the needle at the height of the mucobuccal fold, angled toward the apex (root) of the tooth.",
      "Advance a few millimeters until the tip is near the bone (do not scrape the periosteum excessively, it hurts).",
      "Aspirate, then inject 1-2 mL of anesthetic."
    ],
    "ultrasound": [
      "Not used."
    ],
    "confirmation": [
      "Numbness of the specific tooth and surrounding gingiva."
    ],
    "troubleshooting": [
      "If the block fails, the infection may be altering the local pH, rendering the anesthetic less effective. You may need a true regional block (like an infraorbital or posterior superior alveolar block) further away from the infection."
    ],
    "complications": [
      "Intravascular injection (rare)",
      "Pain at injection site"
    ],
    "aftercare": [
      "Dental follow-up."
    ],
    "documentation": [
      "Specific tooth targeted, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Because the maxilla is porous, you don't need a complex nerve block for upper teeth. Local infiltration above the tooth root works beautifully 95% of the time."
    ]
  },
  {
    "id": "block_auricular",
    "title": "Auricular Block",
    "icon": "lungs",
    "searchTerms": [
      "ear block",
      "auricular"
    ],
    "sections": [
      "Indications",
      "Contraindications",
      "Anatomy",
      "Equipment",
      "Positioning",
      "Steps",
      "Ultrasound",
      "Confirmation",
      "Troubleshooting",
      "Complications",
      "Aftercare",
      "Documentation",
      "Senior Pearls"
    ],
    "reviewTime": "standard",
    "reviewerStatus": "Needs Review",
    "shiftMode": [
      "Target: A 'ring block' around the base of the ear to hit the greater auricular, lesser occipital, and auriculotemporal nerves.",
      "Provides complete anesthesia of the auricle (except the external auditory canal and concha)."
    ],
    "indications": [
      "Complex ear lacerations",
      "Auricular hematoma drainage"
    ],
    "contraindications": [
      "Infection at the injection sites",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The ear is supplied by multiple nerves coming from different directions.",
      "A diamond-shaped ring of subcutaneous anesthetic around the base of the ear blocks them all."
    ],
    "equipment": [
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL of 1% lidocaine or bupivacaine, WITHOUT epinephrine to avoid cartilage ischemia)"
    ],
    "positioning": [
      "Patient seated or in lateral decubitus with the affected ear up."
    ],
    "steps": [
      "Cleanse the skin around the entire ear.",
      "1. Insert the needle just inferior to the earlobe. Inject subcutaneously while tracking anteriorly in front of the tragus.",
      "2. From the same inferior puncture site, track the needle posteriorly behind the earlobe, injecting subcutaneously along the mastoid.",
      "3. Insert the needle just superior to the ear. Track anteriorly to meet the first track.",
      "4. From the superior puncture site, track posteriorly to meet the second track.",
      "You have now created a complete diamond or ring of anesthetic around the base of the ear."
    ],
    "ultrasound": [
      "Not used."
    ],
    "confirmation": [
      "Complete numbness of the auricle (pinna)."
    ],
    "troubleshooting": [
      "If the concha (the bowl of the ear) remains painful, it is because it receives innervation from the vagus/facial nerves deeper inside. A local wheal directly in the concha may be needed."
    ],
    "complications": [
      "Cartilage necrosis (if epinephrine is used, though controversial, best avoided)",
      "Intravascular injection"
    ],
    "aftercare": [
      "Routine wound care or compression dressing (for hematomas)."
    ],
    "documentation": [
      "Volume and type of anesthetic (note NO epinephrine used)."
    ],
    "seniorPearls": [
      "Use a long needle so you only have to poke the patient twice (once at the bottom, once at the top) to complete the entire ring."
    ]
  }
]

def load_data():
    with open(PROCEDURES_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(PROCEDURES_FILE, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load_data()
    existing_ids = set(p["id"] for p in data)
    
    added = 0
    for block in new_blocks:
        if block["id"] not in existing_ids:
            data.append(block)
            added += 1
            
    save_data(data)
    print(f"Added {added} blocks to {PROCEDURES_FILE} (Batch 4)")
