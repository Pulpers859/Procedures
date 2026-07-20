import json
import os

PROCEDURES_FILE = r"C:\Dev\Procedures\Procedures\Resources\procedures.json"

new_blocks = [
  {
    "id": "block_interscalene",
    "title": "Interscalene Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "shoulder block",
      "humerus block",
      "interscalene"
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
      "Target: C5-C7 nerve roots between anterior and middle scalene muscles.",
      "High risk for phrenic nerve palsy (100% block) – avoid in severe COPD/respiratory failure.",
      "Use low volume (10-15 mL) and always visualize needle tip to avoid intravascular/intraneural injection."
    ],
    "indications": [
      "Shoulder dislocation (pre-reduction)",
      "Proximal humerus fracture",
      "Clavicle fracture (lateral third)",
      "Complex shoulder or upper arm lacerations"
    ],
    "contraindications": [
      "Contralateral phrenic nerve palsy or severe baseline pulmonary disease (e.g., severe COPD)",
      "Infection over the injection site",
      "Patient refusal or inability to cooperate",
      "Local anesthetic allergy"
    ],
    "anatomy": [
      "The brachial plexus roots (C5-C7) exit between the anterior and middle scalene muscles.",
      "The 'stoplight' sign: three hypoechoic circles (C5, C6, C7 roots) stacked vertically between the scalene muscles.",
      "The phrenic nerve runs anteriorly over the anterior scalene muscle.",
      "The carotid artery and internal jugular vein are medial to the anterior scalene."
    ],
    "equipment": [
      "Ultrasound machine with high-frequency linear transducer",
      "Sterile ultrasound gel and probe cover",
      "Chlorhexidine skin prep",
      "Regional block needle (echogenic, short bevel, e.g., 21G or 22G, 50mm)",
      "Local anesthetic (e.g., 10-15 mL of 0.25% or 0.5% bupivacaine or ropivacaine)",
      "Normal saline for hydrodissection (optional but recommended)"
    ],
    "positioning": [
      "Patient supine or semi-recumbent with the head turned slightly away from the side to be blocked.",
      "Place the ultrasound machine on the side of the bed opposite the provider for direct line of sight."
    ],
    "steps": [
      "Perform a pre-block neurovascular exam of the upper extremity.",
      "Apply cardiac monitoring if using large volumes, and ensure intralipid is available.",
      "Prep the lateral neck with chlorhexidine.",
      "Place the linear probe transversely over the supraclavicular fossa to identify the subclavian artery and brachial plexus ('bunch of grapes').",
      "Trace the brachial plexus cephalad until it forms the 'stoplight' sign between the anterior and middle scalenes.",
      "Insert the needle in-plane from posterior to anterior (lateral to medial).",
      "Advance the needle through the middle scalene muscle until the tip rests in the interscalene groove.",
      "Aspirate to ensure no vascular puncture, then inject 1-2 mL to confirm spread (hydrodissection).",
      "Inject the remaining anesthetic in 3-5 mL aliquots, aspirating between each, targeting the space around C5-C7.",
      "Withdraw the needle and apply a sterile dressing."
    ],
    "ultrasound": [
      "Identify the carotid artery medially and the sternocleidomastoid (SCM) superficially.",
      "The anterior scalene muscle lies deep to the SCM and lateral to the internal jugular vein.",
      "The middle scalene muscle is lateral to the anterior scalene.",
      "The nerve roots appear as hypoechoic, round structures in the fascial plane between the two scalene muscles."
    ],
    "confirmation": [
      "Anechoic fluid seen spreading around the C5-C7 nerve roots in the interscalene groove.",
      "Patient reports subjective loss of sensation over the shoulder/deltoid.",
      "Motor weakness in shoulder abduction (deltoid) and elbow flexion (biceps)."
    ],
    "troubleshooting": [
      "If the needle is difficult to see: adjust the angle of incidence, use heel-toe maneuvers, or jiggle the needle slightly.",
      "If injection pressure is high or patient reports severe pain/paresthesia: stop immediately (possible intraneural injection). Withdraw 1-2 mm and try again.",
      "If the phrenic nerve is inadvertently blocked (expected complication): reassure the patient, monitor oxygenation, and support breathing if necessary."
    ],
    "complications": [
      "Phrenic nerve palsy (hemidiaphragmatic paresis) - expected in up to 100% of cases",
      "Horner syndrome (stellate ganglion block) - transient ptosis, miosis, anhidrosis",
      "Recurrent laryngeal nerve block (hoarseness)",
      "Intravascular injection (vertebral or carotid artery) causing LAST",
      "Pneumothorax (if needle advanced too far inferiorly/medially)",
      "Peripheral nerve injury"
    ],
    "aftercare": [
      "Monitor the patient for at least 30 minutes for signs of LAST.",
      "Place the arm in a sling to prevent traction injuries to the anesthetized limb.",
      "Educate the patient about the expected duration of numbness and weakness.",
      "Document the post-block neurovascular exam."
    ],
    "documentation": [
      "Indications, consent (written or verbal per policy), and pre-block neurovascular exam.",
      "Anesthetic used (type, volume, concentration).",
      "Ultrasound guidance confirming spread in the interscalene groove.",
      "No vascular puncture or intraneural injection.",
      "Post-block neurovascular exam and absence of immediate complications."
    ],
    "seniorPearls": [
      "Tracing the plexus up from the supraclavicular fossa is often easier than starting directly at the neck.",
      "You don't need to surround every root perfectly. Injecting into the general fascial plane is usually sufficient.",
      "Always assume you will block the phrenic nerve; do not do this block bilaterally."
    ]
  },
  {
    "id": "block_supraclavicular",
    "title": "Supraclavicular Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "arm block",
      "supraclavicular",
      "brachial plexus"
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
      "The 'spinal of the arm' - covers distal humerus, elbow, forearm, wrist, and hand.",
      "Target: Brachial plexus trunks/divisions ('bunch of grapes') lateral and superficial to the subclavian artery.",
      "High risk for pneumothorax (pleura is just deep to the artery) - always visualize the needle tip!"
    ],
    "indications": [
      "Fractures of the distal humerus, elbow, forearm, wrist, or hand",
      "Complex lacerations or amputations of the upper extremity",
      "Painful procedures involving the arm below the mid-humerus"
    ],
    "contraindications": [
      "Severe baseline pulmonary disease (risk of phrenic nerve palsy or pneumothorax)",
      "Infection over the injection site",
      "Patient refusal or inability to cooperate",
      "Local anesthetic allergy"
    ],
    "anatomy": [
      "The brachial plexus at this level is tightly bundled ('bunch of grapes') lateral and superficial to the subclavian artery.",
      "The subclavian artery rests on the first rib.",
      "The pleura (hyperechoic line with lung sliding) lies immediately deep to the first rib and medial to the artery.",
      "The 'corner pocket' is the space between the first rib, subclavian artery, and the brachial plexus."
    ],
    "equipment": [
      "Ultrasound machine with high-frequency linear transducer",
      "Sterile ultrasound gel and probe cover",
      "Chlorhexidine skin prep",
      "Regional block needle (echogenic, short bevel, e.g., 21G or 22G, 50mm)",
      "Local anesthetic (e.g., 15-20 mL of 0.25% or 0.5% bupivacaine or ropivacaine)",
      "Normal saline for hydrodissection"
    ],
    "positioning": [
      "Patient supine or semi-recumbent, head turned slightly away.",
      "Arm resting comfortably at the side or across the abdomen."
    ],
    "steps": [
      "Perform a pre-block neurovascular exam.",
      "Apply cardiac monitoring and ensure intralipid is available.",
      "Prep the supraclavicular fossa.",
      "Place the probe transversely in the supraclavicular fossa, aiming caudally to identify the subclavian artery, first rib, and pleura.",
      "Identify the brachial plexus lateral to the artery.",
      "Insert the needle in-plane from lateral to medial, aiming for the 'corner pocket' (the area deep to the plexus, superficial to the first rib, lateral to the artery).",
      "Aspirate, then inject 1-2 mL of saline to confirm position.",
      "Inject 10-15 mL in the corner pocket.",
      "Withdraw the needle slightly and redirect to the superficial aspect of the plexus to inject the remaining 5-10 mL.",
      "Remove the needle and apply a dressing."
    ],
    "ultrasound": [
      "Subclavian artery: large, pulsatile, anechoic circle.",
      "First rib: hyperechoic line with posterior acoustic shadowing just deep to the artery.",
      "Pleura: hyperechoic line medial to the rib, showing lung sliding.",
      "Brachial plexus: hypoechoic, honeycomb-like structure ('bunch of grapes') lateral/superficial to the artery."
    ],
    "confirmation": [
      "Anechoic fluid spreading around the brachial plexus, especially expanding the 'corner pocket'.",
      "Loss of sensation and motor function in the arm below the mid-humerus."
    ],
    "troubleshooting": [
      "If the first rib is not visible, do not advance the needle. The pleura is directly underneath.",
      "If the needle is lost, stop. Do not advance blindly. Use saline hydrodissection to locate the tip.",
      "To avoid the artery, aim the needle intentionally toward the first rib (bouncing off the rib into the corner pocket is safer than aiming at the artery)."
    ],
    "complications": [
      "Pneumothorax (most feared complication if needle goes too deep/medial)",
      "Phrenic nerve palsy (less common than interscalene, but still ~50%)",
      "Intravascular injection (subclavian artery/vein) causing LAST",
      "Peripheral nerve injury",
      "Horner syndrome"
    ],
    "aftercare": [
      "Monitor for at least 30 minutes.",
      "Place the arm in a sling to prevent traction injury.",
      "Assess for shortness of breath (pneumothorax or phrenic nerve palsy).",
      "Document post-block exam."
    ],
    "documentation": [
      "Consent, indications, and pre-block exam.",
      "Anesthetic used.",
      "Ultrasound guidance confirming spread in the corner pocket and around the plexus.",
      "First rib visualized and pleura avoided.",
      "No vascular puncture or intraneural injection."
    ],
    "seniorPearls": [
      "Aim for the first rib. If you hit the rib, you know you are safe from the pleura. Then slide up into the corner pocket.",
      "Injecting the corner pocket first floats the plexus up and makes the rest of the block easier and safer."
    ]
  },
  {
    "id": "block_raptir",
    "title": "RAPTIR (Infraclavicular) Block",
    "icon": "lungs",
    "searchTerms": [
      "raptir",
      "infraclavicular",
      "arm block"
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
      "Retroclavicular Approach to the Infraclavicular Region (RAPTIR).",
      "Excellent for forearm/hand trauma without the pneumothorax/phrenic risk of supraclavicular blocks.",
      "Target: Axillary artery posterior to the pectoralis minor. The cords surround the artery."
    ],
    "indications": [
      "Fractures of the forearm, wrist, or hand",
      "Complex lacerations or amputations below the elbow",
      "Patients where phrenic nerve palsy or pneumothorax risk is unacceptable (e.g., severe COPD)"
    ],
    "contraindications": [
      "Infection over the injection site",
      "Patient refusal or inability to cooperate",
      "Local anesthetic allergy",
      "Coagulopathy (infraclavicular area is less compressible)"
    ],
    "anatomy": [
      "The brachial plexus cords (lateral, posterior, medial) surround the axillary artery deep to the pectoralis major and minor muscles.",
      "The RAPTIR approach involves inserting the needle posterior to the clavicle, advancing caudally into the infraclavicular space."
    ],
    "equipment": [
      "Ultrasound machine with high-frequency linear or curvilinear transducer (depending on depth)",
      "Sterile ultrasound gel and probe cover",
      "Chlorhexidine skin prep",
      "Regional block needle (echogenic, longer needle required, e.g., 21G 80-100mm)",
      "Local anesthetic (e.g., 20-30 mL of 0.25% or 0.5% bupivacaine or ropivacaine)"
    ],
    "positioning": [
      "Patient supine, head neutral or turned slightly away.",
      "Arm adducted and resting on the abdomen."
    ],
    "steps": [
      "Perform a pre-block neurovascular exam.",
      "Apply cardiac monitoring and ensure intralipid is available.",
      "Place the transducer in the sagittal plane over the infraclavicular fossa to identify the axillary artery and vein deep to the pectoralis muscles.",
      "Prep the skin posterior to the clavicle.",
      "Insert the needle posterior to the clavicle, aiming caudally, strictly in-plane with the transducer.",
      "Advance the needle under the clavicle, visualizing the tip as it enters the ultrasound beam in the infraclavicular space.",
      "Aim for the posterior aspect of the axillary artery (approx. 6 o'clock position).",
      "Aspirate and inject a small test dose of saline.",
      "Inject 20-30 mL of anesthetic, aiming to create a U-shaped spread around the artery.",
      "Withdraw the needle and apply a dressing."
    ],
    "ultrasound": [
      "Pectoralis major (superficial) and pectoralis minor (deep).",
      "Axillary artery is a pulsatile anechoic circle deep to the muscles.",
      "Axillary vein is usually medial/caudal to the artery.",
      "The cords appear as hyperechoic dots surrounding the artery (lateral, posterior, medial)."
    ],
    "confirmation": [
      "Anechoic fluid spreading in a U-shape or completely surrounding the axillary artery.",
      "Loss of sensation and motor function in the arm below the elbow."
    ],
    "troubleshooting": [
      "If the needle trajectory is unclear, withdraw and redirect. The clavicle can obstruct the view if the probe is too close.",
      "If the vein is in the way, adjust the angle or use less probe pressure to avoid compressing it entirely (making it invisible).",
      "If spread is only on one side of the artery, consider a second injection site to surround it, though large volume often spreads sufficiently."
    ],
    "complications": [
      "Vascular puncture (axillary artery/vein) causing hematoma or LAST",
      "Peripheral nerve injury",
      "Pneumothorax (rare, less risk than supraclavicular)"
    ],
    "aftercare": [
      "Monitor for at least 30 minutes.",
      "Place the arm in a sling to prevent traction injury.",
      "Document post-block exam."
    ],
    "documentation": [
      "Consent, indications, and pre-block exam.",
      "Anesthetic used.",
      "Ultrasound guidance confirming spread around the axillary artery.",
      "No vascular puncture.",
      "Post-block neurovascular exam."
    ],
    "seniorPearls": [
      "The RAPTIR approach provides a fantastic in-plane view of the needle approaching the artery, unlike traditional infraclavicular approaches.",
      "Aiming posterior to the artery (6 o'clock) usually ensures the local anesthetic spreads to all three cords."
    ]
  },
  {
    "id": "block_radial_nerve",
    "title": "Radial Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "radial",
      "forearm block"
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
      "Target: Radial nerve in the spiral groove of the humerus or at the elbow joint.",
      "Provides anesthesia to the dorsal thumb, index, and lateral middle finger.",
      "Combine with Median/Ulnar for complete hand anesthesia."
    ],
    "indications": [
      "Lacerations or fractures of the dorsal hand (radial aspect)",
      "Procedures on the thumb or index finger (dorsal)"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "At the elbow, the radial nerve is located between the brachialis and brachioradialis muscles.",
      "Higher up, it wraps around the humerus in the spiral groove."
    ],
    "equipment": [
      "High-frequency linear ultrasound transducer",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL)"
    ],
    "positioning": [
      "Arm supinated and extended, resting comfortably."
    ],
    "steps": [
      "Identify the nerve in short axis at the level of the elbow crease.",
      "Insert the needle in-plane.",
      "Aspirate, then inject 5-10 mL of anesthetic around the nerve."
    ],
    "ultrasound": [
      "Look for the 'honeycomb' appearance of the nerve between the brachialis (medial) and brachioradialis (lateral)."
    ],
    "confirmation": [
      "Anesthetic surrounding the nerve circumferentially.",
      "Numbness in the radial nerve distribution."
    ],
    "troubleshooting": [
      "If the nerve is hard to find at the elbow, scan proximally up the lateral arm."
    ],
    "complications": [
      "Intravascular injection",
      "Nerve injury"
    ],
    "aftercare": [
      "Protect the anesthetized limb."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Blocking at the elbow covers more branches than blocking at the wrist."
    ]
  },
  {
    "id": "block_median_nerve",
    "title": "Median Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "median",
      "forearm block",
      "carpal tunnel"
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
      "Target: Median nerve in the mid-forearm, between FDS and FDP.",
      "Provides anesthesia to the palmar thumb, index, middle, and radial half of ring finger."
    ],
    "indications": [
      "Palmar lacerations",
      "Volar finger fractures/dislocations"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "In the mid-forearm, the median nerve lies between the flexor digitorum superficialis (FDS) and flexor digitorum profundus (FDP)."
    ],
    "equipment": [
      "High-frequency linear ultrasound transducer",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL)"
    ],
    "positioning": [
      "Arm supinated and extended."
    ],
    "steps": [
      "Identify the nerve in short axis in the mid-forearm.",
      "Insert the needle in-plane or out-of-plane.",
      "Aspirate, then inject 5-10 mL of anesthetic to separate the fascial planes."
    ],
    "ultrasound": [
      "Look for a hyperechoic, oval structure between the muscle bellies of the FDS and FDP."
    ],
    "confirmation": [
      "Anesthetic spreading in the fascial plane around the nerve."
    ],
    "troubleshooting": [
      "Have the patient flex their fingers to identify the FDS/FDP muscles sliding; the nerve will remain stationary."
    ],
    "complications": [
      "Intravascular injection (rare here)",
      "Nerve injury"
    ],
    "aftercare": [
      "Protect the anesthetized limb."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Avoid blocking at the wrist (carpal tunnel) due to limited space and higher risk of nerve injury. The mid-forearm is much safer."
    ]
  },
  {
    "id": "block_ulnar_nerve",
    "title": "Ulnar Nerve Block",
    "icon": "lungs",
    "searchTerms": [
      "ulnar",
      "forearm block"
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
      "Target: Ulnar nerve in the mid-to-distal forearm, medial to the ulnar artery.",
      "Provides anesthesia to the 5th digit and medial half of the 4th digit."
    ],
    "indications": [
      "Boxer's fractures",
      "Lacerations or injuries to the ulnar aspect of the hand"
    ],
    "contraindications": [
      "Infection at the injection site",
      "Allergy to local anesthetic"
    ],
    "anatomy": [
      "In the mid-forearm, the ulnar nerve lies just medial (ulnar) to the ulnar artery, deep to the flexor carpi ulnaris (FCU)."
    ],
    "equipment": [
      "High-frequency linear ultrasound transducer",
      "25G or 27G needle (1.5 inch)",
      "Local anesthetic (5-10 mL)"
    ],
    "positioning": [
      "Arm supinated and extended."
    ],
    "steps": [
      "Identify the ulnar artery in the mid-to-distal forearm.",
      "Identify the ulnar nerve immediately medial to the artery.",
      "Insert the needle in-plane, approaching from the medial side.",
      "Aspirate, then inject 5-10 mL of anesthetic around the nerve."
    ],
    "ultrasound": [
      "The nerve is a hyperechoic honeycomb structure next to the pulsatile, anechoic ulnar artery."
    ],
    "confirmation": [
      "Anesthetic spreading between the nerve and the artery, and around the nerve."
    ],
    "troubleshooting": [
      "If the nerve and artery are too close, inject a small amount of saline or anesthetic to dissect them apart before fully surrounding the nerve."
    ],
    "complications": [
      "Intravascular injection (ulnar artery)",
      "Nerve injury"
    ],
    "aftercare": [
      "Protect the anesthetized limb."
    ],
    "documentation": [
      "Pre/post neurovascular exam, volume and type of anesthetic."
    ],
    "seniorPearls": [
      "Block higher up in the forearm to ensure you catch the dorsal cutaneous branch of the ulnar nerve, which branches off proximal to the wrist."
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
    print(f"Added {added} blocks to {PROCEDURES_FILE}")
