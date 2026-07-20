import json

PROCEDURES_FILE = r"C:\Dev\Procedures\Procedures\Resources\procedures.json"

new_blocks = [
  {
    "id": "block_superficial_cervical_plexus",
    "title": "Superficial Cervical Plexus Block",
    "icon": "lungs",
    "searchTerms": [
      "neck block",
      "clavicle block",
      "cervical"
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
      "Target: Superficial cervical plexus as it emerges behind the posterior border of the sternocleidomastoid (SCM) muscle.",
      "Provides anesthesia to the anterior/lateral neck, clavicle, and skin over the shoulder."
    ],
    "indications": [
      "Clavicle fractures",
      "Laceration repairs of the anterior/lateral neck or earlobe",
      "Internal jugular vein cannulation (pain control)"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The plexus wraps around the posterior border of the SCM at approximately its midpoint.",
      "The external jugular vein typically crosses the SCM near this level."
    ],
    "equipment": [
      "High-frequency linear ultrasound transducer",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL, e.g., 1% lidocaine or 0.25% bupivacaine)"
    ],
    "positioning": [
      "Patient supine, head turned away from the side being blocked."
    ],
    "steps": [
      "Place the transducer transversely over the mid-SCM.",
      "Identify the posterior border of the SCM.",
      "Insert the needle in-plane from posterior to anterior.",
      "Aspirate, then inject 5-10 mL of anesthetic in the fascial plane immediately deep to the posterior border of the SCM."
    ],
    "ultrasound": [
      "SCM is the large superficial muscle. Deep to it is the levator scapulae or scalenes.",
      "The plexus often appears as a small hyperechoic cluster at the posterior edge of the SCM."
    ],
    "confirmation": [
      "Anesthetic spreading along the posterior border of the SCM, separating the fascial layers.",
      "Numbness over the neck and clavicle."
    ],
    "troubleshooting": [
      "If the needle tip is not visible, use hydrodissection with small amounts of saline.",
      "Avoid going too deep to prevent a deep cervical plexus block or phrenic nerve block."
    ],
    "complications": [
      "Intravascular injection (EJV or deeper vessels)",
      "Phrenic nerve block (if injection is too deep/voluminous)",
      "Horner syndrome"
    ],
    "aftercare": [
      "Monitor for 30 minutes, especially for dyspnea (phrenic nerve involvement)."
    ],
    "documentation": [
      "Consent, indications, anesthetic volume/type, absence of complications."
    ],
    "seniorPearls": [
      "This is an extremely superficial block. Do not plunge the needle deep to the SCM."
    ]
  },
  {
    "id": "block_serratus_anterior",
    "title": "Serratus Anterior Plane Block",
    "icon": "lungs",
    "searchTerms": [
      "rib block",
      "serratus",
      "chest tube block"
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
      "Target: Fascial plane superficial OR deep to the serratus anterior muscle.",
      "Provides analgesia to the lateral chest wall (T3-T9).",
      "Essential for multi-level rib fractures or chest tube placement."
    ],
    "indications": [
      "Multiple rib fractures (lateral/anterior)",
      "Tube thoracostomy (chest tube) placement",
      "Chest wall abscesses or lacerations"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The latissimus dorsi is the most superficial muscle on the lateral chest wall. The serratus anterior is deep to it, sitting on the ribs.",
      "The thoracodorsal artery and long thoracic nerve run in the plane superficial to the serratus anterior."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine or ropivacaine)"
    ],
    "positioning": [
      "Patient supine or lateral decubitus, arm abducted to expose the lateral chest (axilla)."
    ],
    "steps": [
      "Place the transducer in the mid-axillary line at the 4th or 5th intercostal space (sagittal orientation).",
      "Identify the latissimus dorsi, serratus anterior, ribs, and pleura.",
      "Insert the needle in-plane from cranial to caudal (or caudal to cranial).",
      "Advance into the fascial plane either superficial to the serratus anterior (between latissimus and serratus) OR deep to the serratus anterior (between serratus and ribs).",
      "Aspirate, then inject 20-30 mL of anesthetic."
    ],
    "ultrasound": [
      "Latissimus dorsi (superficial), Serratus anterior (middle), Ribs with posterior shadowing (deep), Pleura (deep to ribs with sliding).",
      "Look for the thoracodorsal artery in the superficial plane to avoid it."
    ],
    "confirmation": [
      "Anechoic fluid spreading linearly along the fascial plane, unzipping the muscles.",
      "Pain relief over the lateral chest wall."
    ],
    "troubleshooting": [
      "If the pleura is not clearly visualized, slide up or down until a rib is clearly in view. Always aim your needle towards a rib to prevent pleural puncture."
    ],
    "complications": [
      "Pneumothorax (if needle goes deep between ribs)",
      "LAST (due to large volume)",
      "Intravascular injection"
    ],
    "aftercare": [
      "Monitor for LAST for 30-60 minutes.",
      "Assess for pneumothorax if patient becomes symptomatic."
    ],
    "documentation": [
      "Consent, indications, large volume anesthetic, confirmation of fascial spread, absence of pneumothorax."
    ],
    "seniorPearls": [
      "Aiming for the rib (deep to serratus) is often safer and provides an excellent block. 'Hit the rib, slide off, inject.'"
    ]
  },
  {
    "id": "block_thoracic_esp",
    "title": "Thoracic Erector Spinae Plane (ESP) Block",
    "icon": "lungs",
    "searchTerms": [
      "esp",
      "erector spinae",
      "posterior rib block"
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
      "Target: Fascial plane deep to the erector spinae muscle, resting on the transverse processes.",
      "Provides somatic and visceral analgesia for posterior/lateral/anterior chest wall."
    ],
    "indications": [
      "Posterior or multiple rib fractures",
      "Herpes zoster (shingles) pain",
      "Thoracic spine fractures (lateral to midline)"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The erector spinae muscle runs vertically along the spine.",
      "The transverse processes (TP) project laterally from the vertebral bodies.",
      "Injecting deep to the erector spinae muscle allows anesthetic to spread cranio-caudally and into the paravertebral space."
    ],
    "equipment": [
      "High-frequency linear or curvilinear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine or ropivacaine)"
    ],
    "positioning": [
      "Patient sitting up or in lateral decubitus position.",
      "Identify the spinous processes and move ~3 cm laterally to find the TPs."
    ],
    "steps": [
      "Place the transducer in a sagittal orientation about 3 cm lateral to the thoracic spinous processes.",
      "Identify the erector spinae muscle and the square, blocky shadows of the transverse processes.",
      "Insert the needle in-plane (usually cranial to caudal).",
      "Advance until the needle tip touches the bony contour of a transverse process.",
      "Aspirate, then inject 20-30 mL of anesthetic."
    ],
    "ultrasound": [
      "Transverse processes appear as square or rectangular hyperechoic structures with posterior shadowing (unlike the rounded ribs).",
      "Erector spinae is the thick muscle layer superficial to the TPs."
    ],
    "confirmation": [
      "Anechoic fluid unzipping the erector spinae muscle off the transverse processes."
    ],
    "troubleshooting": [
      "If you see the pleura between the bony shadows, you are too lateral (on the ribs). Move medially to find the TPs."
    ],
    "complications": [
      "LAST (large volume block)",
      "Pneumothorax (if too lateral and deep)",
      "Epidural or subarachnoid spread (rare but possible)"
    ],
    "aftercare": [
      "Monitor for LAST for 30-60 minutes."
    ],
    "documentation": [
      "Consent, volume of anesthetic, confirmation of spread over transverse process, absence of pneumothorax."
    ],
    "seniorPearls": [
      "The ESP block is remarkably safe because the target is bone (the TP), keeping you far from the pleura if identified correctly."
    ]
  },
  {
    "id": "block_tap",
    "title": "Transversus Abdominis Plane (TAP) Block",
    "icon": "lungs",
    "searchTerms": [
      "tap",
      "abdomen block",
      "abdominal wall"
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
      "Target: Fascial plane between the internal oblique and transversus abdominis muscles.",
      "Provides analgesia to the anterior abdominal wall (parietal peritoneum and skin)."
    ],
    "indications": [
      "Appendicitis pain (pre-op)",
      "Abdominal wall abscesses or lacerations",
      "Post-operative abdominal pain"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The lateral abdominal wall consists of three muscle layers: external oblique (superficial), internal oblique (middle), and transversus abdominis (deep).",
      "The nerves supplying the abdominal wall run in the plane between the internal oblique and transversus abdominis."
    ],
    "equipment": [
      "High-frequency linear or curvilinear transducer",
      "Regional block needle (21G or 22G, 80-100mm)",
      "Local anesthetic (large volume: 20-30 mL of 0.25% bupivacaine or ropivacaine per side)"
    ],
    "positioning": [
      "Patient supine, abdomen exposed."
    ],
    "steps": [
      "Place the transducer transversely on the lateral abdominal wall, midway between the costal margin and the iliac crest (mid-axillary line).",
      "Identify the three muscle layers.",
      "Insert the needle in-plane from anterior to posterior (or vice-versa).",
      "Advance the needle until the tip pops through the fascia of the internal oblique into the TAP plane.",
      "Aspirate, then inject 20-30 mL of anesthetic."
    ],
    "ultrasound": [
      "Look for the 'three stripes' of muscle. The deepest stripe (transversus abdominis) sits right above the peritoneum/bowel."
    ],
    "confirmation": [
      "Anechoic fluid spreading linearly, creating a black elliptical space separating the internal oblique and transversus abdominis."
    ],
    "troubleshooting": [
      "If you only see two muscle layers, you may be too far anterior (rectus sheath) or too far posterior. Move towards the mid-axillary line."
    ],
    "complications": [
      "Intraperitoneal injection / Bowel puncture (if needle goes too deep)",
      "LAST (large volume block)",
      "Liver/spleen injury (rare, if performed too high)"
    ],
    "aftercare": [
      "Monitor for LAST for 30-60 minutes."
    ],
    "documentation": [
      "Consent, confirmation of the three muscle layers, visualization of spread in the correct plane, absence of intraperitoneal injection."
    ],
    "seniorPearls": [
      "This block only covers somatic pain (abdominal wall), not visceral pain (the inflamed organ itself). Patients will still have some deep pain."
    ]
  },
  {
    "id": "block_pecs",
    "title": "PECS I / II Block",
    "icon": "lungs",
    "searchTerms": [
      "pecs",
      "chest block",
      "breast block"
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
      "Target: Fascial planes between the pectoralis major and minor (PECS I), and between the pectoralis minor and serratus anterior (PECS II).",
      "Provides analgesia to the anterior chest wall and axilla."
    ],
    "indications": [
      "Anterior chest wall trauma (anterior rib fractures)",
      "Breast abscess incision and drainage",
      "Pectoral muscle tears"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "The pectoralis major is superficial to the pectoralis minor.",
      "The pectoral branch of the thoracoacromial artery runs in the plane between the two muscles (PECS I).",
      "The serratus anterior muscle lies deep to the pectoralis minor, on top of the ribs (PECS II)."
    ],
    "equipment": [
      "High-frequency linear transducer",
      "Regional block needle (21G or 22G, 50-100mm)",
      "Local anesthetic (20-30 mL of 0.25% bupivacaine or ropivacaine)"
    ],
    "positioning": [
      "Patient supine, arm abducted to 90 degrees."
    ],
    "steps": [
      "Place the transducer obliquely on the chest, below the lateral third of the clavicle.",
      "Identify the pectoralis major, pectoralis minor, and the ribs/pleura deep to them.",
      "Insert the needle in-plane from medial to lateral.",
      "For PECS I: Advance the needle into the fascial plane between the pectoralis major and minor. Inject 10 mL.",
      "For PECS II: Advance the needle deeper, through the pectoralis minor, into the fascial plane between the pectoralis minor and the serratus anterior (or ribs). Inject 15-20 mL."
    ],
    "ultrasound": [
      "Pectoralis major (thickest, superficial), Pectoralis minor (deep to major), Serratus anterior/ribs (deepest)."
    ],
    "confirmation": [
      "Anechoic fluid separating the respective muscle layers."
    ],
    "troubleshooting": [
      "Use color Doppler to identify the thoracoacromial artery in the PECS I plane and avoid it."
    ],
    "complications": [
      "Pneumothorax (if needle goes too deep into the pleura)",
      "LAST (large volume block)",
      "Intravascular injection"
    ],
    "aftercare": [
      "Monitor for LAST for 30-60 minutes."
    ],
    "documentation": [
      "Consent, volume injected in each plane, absence of pneumothorax."
    ],
    "seniorPearls": [
      "Always keep the needle tip in view when passing through the pectoralis minor, as the pleura is just beneath the next muscle layer."
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
    print(f"Added {added} blocks to {PROCEDURES_FILE} (Batch 2)")
