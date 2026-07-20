import json

PROCEDURES_FILE = r"C:\Dev\Procedures\Procedures\Resources\procedures.json"

new_blocks = [
  {
    "id": "block_femoral_nerve",
    "title": "Femoral Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "femoral",
      "leg block",
      "femur fracture"
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
      "Target: Femoral nerve lateral to the femoral artery, deep to the fascia iliaca.",
      "Provides anesthesia to the anterior thigh, femur, and knee.",
      "Mnemonic: NAVEL (from lateral to medial: Nerve, Artery, Vein, Empty space, Lymphatics)."
    ],
    "indications": [
      "Femur fractures (mid-shaft)",
      "Patellar fractures or severe knee trauma",
      "Large lacerations on the anterior thigh"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The femoral nerve lies lateral to the femoral artery in the femoral triangle, just distal to the inguinal ligament.",
      "It is covered by the fascia iliaca."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (15-20 mL of 0.25% or 0.5% bupivacaine)"
    ],
    "positioning": [
      "Patient supine, leg extended."
    ],
    "steps": [
      "Place the transducer transversely over the femoral crease.",
      "Identify the femoral artery and vein.",
      "Identify the femoral nerve lateral to the artery as a hyperechoic, triangular or oval structure.",
      "Insert the needle in-plane from lateral to medial.",
      "Advance the needle until the tip pops through the fascia iliaca, aiming adjacent to the nerve.",
      "Aspirate, then inject 15-20 mL of anesthetic."
    ],
    "ultrasound": [
      "Femoral artery is a pulsatile, anechoic circle.",
      "The nerve is a hyperechoic cluster lateral to the artery, often appearing triangular or oval."
    ],
    "confirmation": [
      "Anechoic fluid surrounding the nerve beneath the fascia iliaca.",
      "Loss of sensation over the anterior thigh and weakness in knee extension (quadriceps)."
    ],
    "troubleshooting": [
      "If the nerve is hard to distinguish from fat or connective tissue, tilt the probe to enhance anisotropy.",
      "If fluid spreads superficial to the fascia iliaca, withdraw slightly and redirect deeper."
    ],
    "complications": [
      "Intravascular injection (femoral artery or vein)",
      "Nerve injury"
    ],
    "aftercare": [
      "Patient will have significant quadriceps weakness and a high fall risk. Strict non-weight-bearing until the block wears off."
    ],
    "documentation": [
      "Consent, volume of anesthetic, confirmation of spread below fascia iliaca, warnings given regarding fall risk."
    ],
    "seniorPearls": [
      "Always document that you told the patient they cannot walk on that leg. The quad weakness is profound."
    ]
  },
  {
    "id": "block_peng",
    "title": "PENG (Pericapsular Nerve Group) Block",
    "icon": "lungs",
    "searchTerms": [
      "peng",
      "hip fracture",
      "pelvis"
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
      "Target: Fascial plane between the psoas tendon and the pubic ramus.",
      "Provides excellent analgesia for the hip joint (articular branches of femoral and obturator nerves).",
      "Motor-sparing alternative to the fascia iliaca or femoral nerve block."
    ],
    "indications": [
      "Hip fractures (neck of femur, intertrochanteric)",
      "Pelvic fractures involving the acetabulum"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The articular branches of the femoral, obturator, and accessory obturator nerves supply the anterior hip capsule.",
      "These nerves run in the space between the psoas muscle/tendon and the iliopubic eminence."
    ],
    "equipment": [
      "Curvilinear or low-frequency linear transducer (due to depth)",
      "Regional block needle (21G or 22G, 80-100mm)",
      "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine)"
    ],
    "positioning": [
      "Patient supine."
    ],
    "steps": [
      "Place the transducer in a transverse plane over the Anterior Inferior Iliac Spine (AIIS), then slide caudally to find the iliopubic eminence (IPE) and psoas tendon.",
      "Identify the femoral artery/vein sitting medially.",
      "Insert the needle in-plane from lateral to medial.",
      "Advance the needle tip until it rests on the bony contour of the IPE, deep to the psoas tendon.",
      "Aspirate, then inject 20-30 mL of anesthetic."
    ],
    "ultrasound": [
      "The bony contour shows the rounded AIIS transitioning into the more flattened IPE.",
      "The thick psoas muscle sits directly on the bone.",
      "The femoral vessels are medial."
    ],
    "confirmation": [
      "Anechoic fluid lifting the psoas muscle off the bone."
    ],
    "troubleshooting": [
      "Ensure you are deep to the psoas tendon. If the fluid injects into the muscle belly, you are too superficial."
    ],
    "complications": [
      "Intravascular injection",
      "LAST (large volume block)"
    ],
    "aftercare": [
      "Monitor for LAST for 30-60 minutes."
    ],
    "documentation": [
      "Consent, volume of anesthetic, confirmation of spread deep to psoas tendon."
    ],
    "seniorPearls": [
      "The PENG block is fantastic for hip fractures because it is largely motor-sparing, unlike a femoral or fascia iliaca block which paralyzes the quad."
    ]
  },
  {
    "id": "block_saphenous_nerve",
    "title": "Saphenous Nerve (Adductor Canal) Block",
    "icon": "lungs",
    "searchTerms": [
      "saphenous",
      "adductor canal",
      "knee block"
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
      "Target: Saphenous nerve in the adductor canal.",
      "Provides sensory analgesia to the medial lower leg and ankle.",
      "Purely sensory branch of the femoral nerve (motor-sparing)."
    ],
    "indications": [
      "Lacerations or fractures of the medial lower leg",
      "Medial ankle fractures (often combined with popliteal sciatic)"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The saphenous nerve travels with the superficial femoral artery in the adductor canal, deep to the sartorius muscle."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (10-15 mL)"
    ],
    "positioning": [
      "Patient supine, leg slightly externally rotated ('frog leg' position)."
    ],
    "steps": [
      "Place the transducer transversely on the mid-medial thigh.",
      "Identify the sartorius muscle (boat-shaped).",
      "Deep to the sartorius, identify the femoral artery and vein.",
      "The saphenous nerve is often visible as a small hyperechoic dot anterior/lateral to the artery.",
      "Insert the needle in-plane from anterior to posterior (or lateral to medial).",
      "Advance through the sartorius muscle or vastus medialis into the fascial plane surrounding the artery.",
      "Aspirate, then inject 10-15 mL of anesthetic."
    ],
    "ultrasound": [
      "Sartorius is the most superficial muscle on the anteromedial thigh.",
      "The artery is pulsatile and anechoic just beneath it."
    ],
    "confirmation": [
      "Anechoic fluid surrounding the artery and nerve in the adductor canal.",
      "Loss of sensation on the medial aspect of the lower leg."
    ],
    "troubleshooting": [
      "If the nerve is not visible, simply injecting the local anesthetic around the artery (perivascular spread) within the canal is usually sufficient."
    ],
    "complications": [
      "Intravascular injection"
    ],
    "aftercare": [
      "Protect the anesthetized skin from injury."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Because it's a sensory block, patients can still walk (unlike a femoral nerve block), making it ideal for medial leg/ankle injuries in patients who need to ambulate."
    ]
  },
  {
    "id": "block_popliteal_sciatic",
    "title": "Popliteal Sciatic Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "popliteal",
      "sciatic",
      "ankle block"
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
      "Target: Sciatic nerve in the popliteal fossa before it bifurcates.",
      "Provides anesthesia to the entire lower leg and foot, EXCEPT the medial strip (covered by the saphenous nerve)."
    ],
    "indications": [
      "Achilles tendon ruptures",
      "Ankle and foot fractures (often combined with a saphenous block)",
      "Complex foot lacerations"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The sciatic nerve travels down the posterior thigh.",
      "In the popliteal fossa, it bifurcates into the tibial nerve (medial) and common peroneal nerve (lateral).",
      "The popliteal artery and vein are medial and deep to the nerve."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (20-30 mL)"
    ],
    "positioning": [
      "Patient prone, or lateral decubitus, or supine with the leg elevated."
    ],
    "steps": [
      "Place the transducer transversely over the popliteal crease.",
      "Identify the popliteal artery (deepest), vein (middle), and the tibial and common peroneal nerves (superficial and lateral).",
      "Trace the two nerves proximally (cephalad) until they join into the single sciatic nerve.",
      "Insert the needle in-plane from lateral to medial.",
      "Advance the needle to the sciatic nerve, within its epineural sheath (the 'Vloka sheath').",
      "Aspirate, then inject 20-30 mL of anesthetic."
    ],
    "ultrasound": [
      "The nerves look like hyperechoic honeycombs.",
      "The 'stoplight' sign in the popliteal crease: Artery (deep), Vein (middle), Tibial Nerve (superficial)."
    ],
    "confirmation": [
      "Anechoic fluid spreading circumferentially around the sciatic nerve, often dissecting it back into its two branches.",
      "Loss of sensation over the lateral leg and entire foot (except medial strip)."
    ],
    "troubleshooting": [
      "Injecting just as the nerve bifurcates, inside the common paraneural sheath, provides the most rapid onset."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury"
    ],
    "aftercare": [
      "Patient will have foot drop (inability to dorsiflex). Strictly non-weight-bearing."
    ],
    "documentation": [
      "Consent, volume of anesthetic, warning about foot drop and fall risk."
    ],
    "seniorPearls": [
      "Always combine this with a saphenous nerve block if you need complete anesthesia of the ankle/foot (e.g., for an ankle fracture reduction)."
    ]
  },
  {
    "id": "block_transgluteal_sciatic",
    "title": "Transgluteal / Proximal Sciatic Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "sciatic",
      "gluteal",
      "posterior thigh"
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
      "Target: Sciatic nerve deep in the posterior thigh/gluteal region.",
      "Provides anesthesia to the posterior thigh and the entire lower leg (except medial strip)."
    ],
    "indications": [
      "Posterior thigh lacerations or hamstring tears",
      "Knee trauma requiring posterior capsule analgesia"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The sciatic nerve is large and located deep to the gluteus maximus (or biceps femoris, depending on level) and superficial to the quadratus femoris or adductor magnus."
    ],
    "equipment": [
      "Curvilinear transducer (due to depth)",
      "Regional block needle (21G or 22G, 80-100mm)",
      "Local anesthetic (20-30 mL)"
    ],
    "positioning": [
      "Patient in lateral decubitus position (sims position) or prone."
    ],
    "steps": [
      "Place the transducer transversely below the gluteal fold.",
      "Identify the ischial tuberosity (medial) and the greater trochanter (lateral) if scanning high enough.",
      "Identify the large, hyperechoic, oval sciatic nerve midway between them, deep to the gluteus maximus.",
      "Insert the needle in-plane.",
      "Advance to the nerve, aspirate, and inject 20-30 mL of anesthetic around it."
    ],
    "ultrasound": [
      "The nerve is highly anisotropic and may appear dark depending on probe angle. Heel-toe the probe to make it bright."
    ],
    "confirmation": [
      "Circumferential spread around the nerve."
    ],
    "troubleshooting": [
      "If the nerve is difficult to see, look for the acoustic shadow of the ischial tuberosity and greater trochanter; the nerve is exactly in the middle."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury"
    ],
    "aftercare": [
      "Foot drop will occur. Strictly non-weight-bearing."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume of anesthetic, warning about foot drop."
    ],
    "seniorPearls": [
      "The sciatic nerve at this level is the largest nerve in the body. It takes a significant volume (20-30 mL) and time (up to 30 mins) to fully block."
    ]
  },
  {
    "id": "block_tibial_nerve",
    "title": "Tibial Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "tibial",
      "ankle block",
      "plantar"
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
      "Target: Posterior tibial nerve posterior to the medial malleolus.",
      "Provides anesthesia to the heel and sole (plantar aspect) of the foot."
    ],
    "indications": [
      "Plantar lacerations",
      "Foreign body removal from the sole of the foot"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "Posterior to the medial malleolus. Mnemonic: Tom, Dick, AND Very Nervous Harry (Tibialis posterior, flexor Digitorum longus, Artery, Nerve, Vein, flexor Hallucis longus)."
    ],
    "equipment": [
      "High-frequency linear transducer (or landmark technique)",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL)"
    ],
    "positioning": [
      "Patient supine, foot externally rotated."
    ],
    "steps": [
      "Place transducer transversely behind the medial malleolus.",
      "Identify the posterior tibial artery.",
      "Identify the nerve immediately posterior/lateral to the artery.",
      "Insert the needle in-plane or out-of-plane, aspirate, and inject 5-10 mL around the nerve."
    ],
    "ultrasound": [
      "The artery is the pulsatile anechoic circle; the nerve is the honeycomb structure next to it."
    ],
    "confirmation": [
      "Anechoic fluid surrounding the nerve.",
      "Numbness on the sole of the foot."
    ],
    "troubleshooting": [
      "Use color Doppler to ensure you don't inject into the artery or veins."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury"
    ],
    "aftercare": [
      "Warn the patient about lack of sensation when walking, to avoid unnoticed injuries."
    ],
    "documentation": [
      "Pre/post exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "For a purely plantar laceration, this block is vastly superior to injecting local anesthetic directly into the exquisitely sensitive sole of the foot."
    ]
  },
  {
    "id": "block_sural_nerve",
    "title": "Sural Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "sural",
      "lateral foot",
      "ankle block"
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
      "Target: Sural nerve posterior to the lateral malleolus.",
      "Provides anesthesia to the lateral/posterior aspect of the foot."
    ],
    "indications": [
      "Lacerations on the lateral aspect of the foot"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The sural nerve travels with the small saphenous vein posterior to the lateral malleolus."
    ],
    "equipment": [
      "High-frequency linear transducer (or landmark technique)",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (3-5 mL)"
    ],
    "positioning": [
      "Patient supine, foot internally rotated."
    ],
    "steps": [
      "Place transducer transversely behind the lateral malleolus.",
      "Identify the small saphenous vein.",
      "The nerve is adjacent to the vein.",
      "Inject 3-5 mL of anesthetic around the nerve/vein."
    ],
    "ultrasound": [
      "The vein is easily compressible. The nerve is a tiny honeycomb structure next to it."
    ],
    "confirmation": [
      "Fluid surrounding the nerve.",
      "Numbness on the lateral foot."
    ],
    "troubleshooting": [
      "If using landmarks, simply deposit a subcutaneous wheal of anesthetic from the Achilles tendon to the lateral malleolus."
    ],
    "complications": [
      "Intravascular injection"
    ],
    "aftercare": [
      "Routine wound care."
    ],
    "documentation": [
      "Pre/post exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "The landmark 'subcutaneous wheal' technique is often faster and just as effective as ultrasound for this specific small nerve."
    ]
  },
  {
    "id": "block_superficial_peroneal",
    "title": "Superficial Peroneal Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "superficial peroneal",
      "dorsum foot",
      "ankle block"
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
      "Target: Superficial peroneal nerve on the anterior/lateral aspect of the distal leg.",
      "Provides anesthesia to the dorsum of the foot (except the first web space)."
    ],
    "indications": [
      "Lacerations or procedures on the dorsum of the foot"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The nerve pierces the deep fascia in the distal third of the lateral leg to become superficial."
    ],
    "equipment": [
      "High-frequency linear transducer (or landmark technique)",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL)"
    ],
    "positioning": [
      "Patient supine."
    ],
    "steps": [
      "Place transducer transversely on the anterolateral distal leg.",
      "Identify the nerve as it emerges through the crural fascia.",
      "Inject 5-10 mL of anesthetic around the nerve."
    ],
    "ultrasound": [
      "The nerve is a small hyperechoic structure that pops through the bright fascial line."
    ],
    "confirmation": [
      "Numbness on the dorsum of the foot."
    ],
    "troubleshooting": [
      "For landmarks, inject a subcutaneous band of anesthetic from the anterior tibial crest to the lateral malleolus."
    ],
    "complications": [
      "Intravascular injection"
    ],
    "aftercare": [
      "Routine wound care."
    ],
    "documentation": [
      "Pre/post exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "This nerve branches extensively. A wide subcutaneous band of anesthetic is often needed if using landmarks."
    ]
  },
  {
    "id": "block_deep_peroneal",
    "title": "Deep Peroneal Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "deep peroneal",
      "first web space",
      "ankle block"
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
      "Target: Deep peroneal nerve anterior to the ankle joint.",
      "Provides anesthesia to the first web space (between big toe and second toe)."
    ],
    "indications": [
      "Lacerations or procedures in the first web space of the foot"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The deep peroneal nerve travels with the anterior tibial artery (dorsalis pedis) between the extensor hallucis longus and extensor digitorum longus tendons."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (3-5 mL)"
    ],
    "positioning": [
      "Patient supine."
    ],
    "steps": [
      "Place transducer transversely over the anterior ankle.",
      "Identify the anterior tibial artery.",
      "The nerve is usually lateral to the artery.",
      "Inject 3-5 mL of anesthetic next to the artery."
    ],
    "ultrasound": [
      "Pulsatile artery; nerve is a small honeycomb dot next to it."
    ],
    "confirmation": [
      "Numbness in the first web space."
    ],
    "troubleshooting": [
      "Avoid intravascular injection by carefully aspirating and using color Doppler."
    ],
    "complications": [
      "Intravascular injection"
    ],
    "aftercare": [
      "Routine wound care."
    ],
    "documentation": [
      "Pre/post exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "This nerve is very small. Perivascular spread around the anterior tibial artery is usually sufficient."
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
    print(f"Added {added} blocks to {PROCEDURES_FILE} (Batch 3)")
