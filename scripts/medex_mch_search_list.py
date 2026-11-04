"""
MedEx search list for the Bangla MCH (maternal, newborn, child health) drug-safety KG.

How to use
- `query` is the generic (INN) name to look up in MedEx. Resolve it to a MedEx
  generic page yourself and record the page id/slug in `medex_id`.
- `medex_id_unverified` holds the ids YOU supplied earlier. They were not
  verified against live pages. Fetch each page and check the generic name
  matches before trusting them.
- ATC codes were written from memory. Verify against the WHO ATC index before
  they go into the KG. Class-level codes (4th level) are used where unsure.

Fields
- scope : maternal | newborn | child | contraception
- group : clinical use group
- role  : core      = standard MCH care
          caution   = used, but a documented warning/controversy exists
          contrast  = avoid in pregnancy/lactation (source for contraindication triples)
          antidote  = treats toxicity of a core drug
- tier  : 1 = pilot and benchmark first, 2 = expand after the pilot works
"""

MCH_SEARCH_LIST = [
    # ---- Uterotonics, PPH, abortion/induction ----
    {"query": "oxytocin", "atc": "H01BB02", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 1, "medex_id_unverified": "854"},
    {"query": "carbetocin", "atc": "H01BB03", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "methylergometrine", "atc": "G02AB01", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 1, "medex_id_unverified": "748"},
    {"query": "ergometrine", "atc": "G02AB02", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "may be indexed under methylergometrine"},
    {"query": "misoprostol", "atc": "G02AD06", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 1, "medex_id_unverified": "764", "note": "also contraindicated for NSAID-ulcer use in pregnancy"},
    {"query": "carboprost", "atc": "G02AD04", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 2, "medex_id_unverified": "2263"},
    {"query": "dinoprostone", "atc": "G02AD02", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "tranexamic acid", "atc": "B02AA02", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 1, "medex_id_unverified": None, "note": "WHO-recommended for PPH; missing from first list"},
    {"query": "mifepristone", "atc": "G03XB01", "scope": "maternal", "group": "uterotonic_pph", "role": "core", "tier": 1, "medex_id_unverified": "753", "note": "MR kit generics are separate combination pages"},

    # ---- Progestogens (pregnancy maintenance) ----
    {"query": "progesterone", "atc": "G03DA04", "scope": "maternal", "group": "progestogen", "role": "core", "tier": 1, "medex_id_unverified": "959"},
    {"query": "dydrogesterone", "atc": "G03DB01", "scope": "maternal", "group": "progestogen", "role": "core", "tier": 2, "medex_id_unverified": None},

    # ---- Tocolytics (preterm labour) ----
    {"query": "nifedipine", "atc": "C08CA05", "scope": "maternal", "group": "tocolytic", "role": "core", "tier": 1, "medex_id_unverified": "808", "note": "also an antihypertensive"},
    {"query": "atosiban", "atc": "G02CX01", "scope": "maternal", "group": "tocolytic", "role": "core", "tier": 2, "medex_id_unverified": "1819"},
    {"query": "salbutamol", "atc": "R03AC02", "scope": "maternal", "group": "tocolytic", "role": "core", "tier": 2, "medex_id_unverified": "1002", "note": "also child asthma use"},
    {"query": "terbutaline", "atc": "R03AC03", "scope": "maternal", "group": "tocolytic", "role": "caution", "tier": 1, "medex_id_unverified": "1062", "note": "regulators warn against prolonged tocolysis; good source-disagreement test"},
    {"query": "isoxsuprine", "atc": "C04AA01", "scope": "maternal", "group": "tocolytic", "role": "caution", "tier": 2, "medex_id_unverified": "644"},
    {"query": "indomethacin", "atc": "M01AB01", "scope": "maternal", "group": "tocolytic", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "fetal ductus constriction risk"},

    # ---- Eclampsia ----
    {"query": "magnesium sulfate", "atc": "B05XA05", "scope": "maternal", "group": "eclampsia", "role": "core", "tier": 1, "medex_id_unverified": "713", "note": "MedEx may split injection vs laxative/oral pages"},
    {"query": "calcium gluconate", "atc": "A12AA03", "scope": "maternal", "group": "eclampsia", "role": "antidote", "tier": 1, "medex_id_unverified": None, "note": "antidote for magnesium toxicity"},
    {"query": "diazepam", "atc": "N05BA01", "scope": "maternal", "group": "eclampsia", "role": "core", "tier": 2, "medex_id_unverified": None},

    # ---- Hypertension in pregnancy ----
    {"query": "labetalol", "atc": "C07AG01", "scope": "maternal", "group": "antihypertensive", "role": "core", "tier": 1, "medex_id_unverified": "1821"},
    {"query": "methyldopa", "atc": "C02AB01", "scope": "maternal", "group": "antihypertensive", "role": "core", "tier": 1, "medex_id_unverified": "746"},
    {"query": "hydralazine", "atc": "C02DB02", "scope": "maternal", "group": "antihypertensive", "role": "core", "tier": 1, "medex_id_unverified": "586"},
    {"query": "captopril", "atc": "C09AA01", "scope": "maternal", "group": "antihypertensive", "role": "contrast", "tier": 1, "medex_id_unverified": "218"},
    {"query": "enalapril", "atc": "C09AA02", "scope": "maternal", "group": "antihypertensive", "role": "contrast", "tier": 1, "medex_id_unverified": None},
    {"query": "losartan", "atc": "C09CA01", "scope": "maternal", "group": "antihypertensive", "role": "contrast", "tier": 1, "medex_id_unverified": None},
    {"query": "atenolol", "atc": "C07AB03", "scope": "maternal", "group": "antihypertensive", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "fetal growth restriction concern"},

    # ---- Antenatal corticosteroids ----
    {"query": "betamethasone", "atc": "H02AB01", "scope": "maternal", "group": "antenatal_steroid", "role": "core", "tier": 1, "medex_id_unverified": "183"},
    {"query": "dexamethasone", "atc": "H02AB02", "scope": "maternal", "group": "antenatal_steroid", "role": "core", "tier": 1, "medex_id_unverified": "344"},

    # ---- Antiplatelet / anticoagulant ----
    {"query": "aspirin", "atc": "B01AC06", "scope": "maternal", "group": "anticoagulant_antiplatelet", "role": "core", "tier": 1, "medex_id_unverified": None, "note": "low-dose, preeclampsia prevention; check low-dose pages"},
    {"query": "enoxaparin", "atc": "B01AB05", "scope": "maternal", "group": "anticoagulant_antiplatelet", "role": "core", "tier": 1, "medex_id_unverified": None, "note": "pregnancy-safe contrast to warfarin"},
    {"query": "heparin", "atc": "B01AB01", "scope": "maternal", "group": "anticoagulant_antiplatelet", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "warfarin", "atc": "B01AA03", "scope": "maternal", "group": "anticoagulant_antiplatelet", "role": "contrast", "tier": 1, "medex_id_unverified": "1119"},

    # ---- Nausea / hyperemesis ----
    {"query": "doxylamine + pyridoxine", "atc": None, "scope": "maternal", "group": "antiemetic", "role": "core", "tier": 2, "medex_id_unverified": "393", "note": "combination; confirm it is marketed in Bangladesh"},
    {"query": "ondansetron", "atc": "A04AA01", "scope": "maternal", "group": "antiemetic", "role": "caution", "tier": 2, "medex_id_unverified": "838", "note": "first-trimester safety debated"},
    {"query": "metoclopramide", "atc": "A03FA01", "scope": "maternal", "group": "antiemetic", "role": "core", "tier": 1, "medex_id_unverified": "744"},
    {"query": "prochlorperazine", "atc": "N05AB04", "scope": "maternal", "group": "antiemetic", "role": "core", "tier": 2, "medex_id_unverified": "955"},
    {"query": "promethazine", "atc": "R06AA02", "scope": "maternal", "group": "antiemetic", "role": "core", "tier": 2, "medex_id_unverified": None},

    # ---- Micronutrients, anaemia ----
    {"query": "folic acid", "atc": "B03BB01", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 1, "medex_id_unverified": "499"},
    {"query": "ferrous sulfate", "atc": "B03AA07", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 1, "medex_id_unverified": None},
    {"query": "ferrous fumarate", "atc": "B03AA02", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "iron sucrose", "atc": "B03AC", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "class-level ATC; verify exact code"},
    {"query": "calcium carbonate", "atc": "A12AA04", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "cholecalciferol", "atc": "A11CC05", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "zinc sulfate", "atc": "A12CB01", "scope": "child", "group": "micronutrient", "role": "core", "tier": 1, "medex_id_unverified": None, "note": "child diarrhoea"},
    {"query": "vitamin A (retinol)", "atc": "A11CA01", "scope": "child", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "high-dose vitamin A is a pregnancy concern; good contrast pair"},
    {"query": "cyanocobalamin", "atc": "B03BA01", "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "ferrous ascorbate + folic acid + zinc sulfate", "atc": None, "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": "461", "note": "combination generic"},
    {"query": "folic acid + zinc sulfate monohydrate", "atc": None, "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": "498", "note": "combination generic"},
    {"query": "calcium carbonate + vitamin D3", "atc": None, "scope": "maternal", "group": "micronutrient", "role": "core", "tier": 2, "medex_id_unverified": "214", "note": "combination generic"},

    # ---- Antibiotics and anti-infectives ----
    {"query": "ampicillin", "atc": "J01CA01", "scope": "newborn", "group": "antibiotic", "role": "core", "tier": 1, "medex_id_unverified": "67"},
    {"query": "amoxicillin", "atc": "J01CA04", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 1, "medex_id_unverified": "61", "note": "also child pneumonia"},
    {"query": "amoxicillin + clavulanic acid", "atc": "J01CR02", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "benzathine benzylpenicillin", "atc": "J01CE08", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "syphilis in pregnancy; may not be marketed"},
    {"query": "cefixime", "atc": "J01DD08", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": "230"},
    {"query": "ceftriaxone", "atc": "J01DD04", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 1, "medex_id_unverified": "233"},
    {"query": "cefuroxime", "atc": "J01DC02", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "cefazolin", "atc": "J01DB04", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "caesarean prophylaxis"},
    {"query": "gentamicin", "atc": "J01GB03", "scope": "newborn", "group": "antibiotic", "role": "core", "tier": 1, "medex_id_unverified": "528"},
    {"query": "metronidazole", "atc": "J01XD01", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 1, "medex_id_unverified": "750"},
    {"query": "azithromycin", "atc": "J01FA10", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": "129"},
    {"query": "erythromycin", "atc": "J01FA01", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": "416"},
    {"query": "clindamycin", "atc": "J01FF01", "scope": "maternal", "group": "antibiotic", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "nitrofurantoin", "atc": "J01XE01", "scope": "maternal", "group": "antibiotic", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "avoid near term; UTI in pregnancy"},
    {"query": "sulfamethoxazole + trimethoprim", "atc": "J01EE01", "scope": "maternal", "group": "antibiotic", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "folate antagonism first trimester; kernicterus concern near term"},
    {"query": "doxycycline", "atc": "J01AA02", "scope": "maternal", "group": "antibiotic", "role": "contrast", "tier": 1, "medex_id_unverified": None},
    {"query": "tetracycline", "atc": "J01AA07", "scope": "maternal", "group": "antibiotic", "role": "contrast", "tier": 2, "medex_id_unverified": None},
    {"query": "ciprofloxacin", "atc": "J01MA02", "scope": "maternal", "group": "antibiotic", "role": "contrast", "tier": 2, "medex_id_unverified": None},
    {"query": "fluconazole", "atc": "J02AC01", "scope": "maternal", "group": "antifungal", "role": "contrast", "tier": 2, "medex_id_unverified": None, "note": "high-dose teratogenicity"},
    {"query": "clotrimazole", "atc": "G01AF02", "scope": "maternal", "group": "antifungal", "role": "core", "tier": 2, "medex_id_unverified": "291", "note": "vaginal candidiasis"},
    {"query": "albendazole", "atc": "P02CA03", "scope": "maternal", "group": "anthelmintic", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "avoid first trimester; also child deworming"},
    {"query": "mebendazole", "atc": "P02CA01", "scope": "child", "group": "anthelmintic", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "anti-D immunoglobulin", "atc": "J06BB01", "scope": "maternal", "group": "immunoglobulin", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "may be listed under biologicals"},

    # ---- Analgesics ----
    {"query": "paracetamol", "atc": "N02BE01", "scope": "maternal", "group": "analgesic", "role": "core", "tier": 1, "medex_id_unverified": "860", "note": "also child fever; many brand/dose pages"},
    {"query": "ibuprofen", "atc": "M01AE01", "scope": "maternal", "group": "analgesic", "role": "caution", "tier": 1, "medex_id_unverified": None, "note": "avoid from ~30 weeks; also child fever"},
    {"query": "diclofenac", "atc": "M01AB05", "scope": "maternal", "group": "analgesic", "role": "contrast", "tier": 1, "medex_id_unverified": None},

    # ---- Endocrine ----
    {"query": "insulin (human)", "atc": "A10AB01", "scope": "maternal", "group": "endocrine", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "gestational diabetes"},
    {"query": "metformin", "atc": "A10BA02", "scope": "maternal", "group": "endocrine", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "levothyroxine", "atc": "H03AA01", "scope": "maternal", "group": "endocrine", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "propylthiouracil", "atc": "H03BA02", "scope": "maternal", "group": "endocrine", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "preferred first trimester; may be rarely marketed"},
    {"query": "carbimazole", "atc": "H03BB01", "scope": "maternal", "group": "endocrine", "role": "contrast", "tier": 2, "medex_id_unverified": None, "note": "first-trimester teratogenicity"},

    # ---- Antiepileptics and other teratogens ----
    {"query": "sodium valproate", "atc": "N03AG01", "scope": "maternal", "group": "anticonvulsant", "role": "contrast", "tier": 1, "medex_id_unverified": "1016"},
    {"query": "carbamazepine", "atc": "N03AF01", "scope": "maternal", "group": "anticonvulsant", "role": "contrast", "tier": 2, "medex_id_unverified": None},
    {"query": "phenytoin", "atc": "N03AB02", "scope": "maternal", "group": "anticonvulsant", "role": "contrast", "tier": 2, "medex_id_unverified": None},
    {"query": "lamotrigine", "atc": "N03AX09", "scope": "maternal", "group": "anticonvulsant", "role": "caution", "tier": 2, "medex_id_unverified": None},
    {"query": "levetiracetam", "atc": "N03AX14", "scope": "maternal", "group": "anticonvulsant", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "methotrexate", "atc": "L01BA01", "scope": "maternal", "group": "teratogen", "role": "contrast", "tier": 1, "medex_id_unverified": "740"},
    {"query": "isotretinoin", "atc": "D10BA01", "scope": "maternal", "group": "teratogen", "role": "contrast", "tier": 1, "medex_id_unverified": "647"},
    {"query": "thalidomide", "atc": "L04AX02", "scope": "maternal", "group": "teratogen", "role": "contrast", "tier": 2, "medex_id_unverified": "1068", "note": "confirm it is listed in MedEx"},
    {"query": "atorvastatin", "atc": "C10AA05", "scope": "maternal", "group": "teratogen", "role": "contrast", "tier": 2, "medex_id_unverified": None},
    {"query": "lithium carbonate", "atc": "N05AN01", "scope": "maternal", "group": "teratogen", "role": "contrast", "tier": 2, "medex_id_unverified": None},

    # ---- Newborn ----
    {"query": "phytomenadione (vitamin K)", "atc": "B02BA01", "scope": "newborn", "group": "newborn", "role": "core", "tier": 1, "medex_id_unverified": None},
    {"query": "caffeine citrate", "atc": "N06BC01", "scope": "newborn", "group": "newborn", "role": "core", "tier": 1, "medex_id_unverified": "199"},
    {"query": "phenobarbital", "atc": "N03AA02", "scope": "newborn", "group": "newborn", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "chlorhexidine", "atc": "D08AC02", "scope": "newborn", "group": "newborn", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "cord care; may be 7.1% gel product"},
    {"query": "poractant alfa", "atc": "R07AA02", "scope": "newborn", "group": "newborn", "role": "core", "tier": 2, "medex_id_unverified": None},

    # ---- Child ----
    {"query": "oral rehydration salts", "atc": "A07CA", "scope": "child", "group": "child", "role": "core", "tier": 1, "medex_id_unverified": None, "note": "class-level ATC"},

    # ---- Contraception and postpartum family planning ----
    {"query": "levonorgestrel", "atc": "G03AC03", "scope": "contraception", "group": "contraception", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "ATC differs for emergency use (G03AD01)"},
    {"query": "medroxyprogesterone", "atc": "G03AC06", "scope": "contraception", "group": "contraception", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "etonogestrel", "atc": "G03AC08", "scope": "contraception", "group": "contraception", "role": "core", "tier": 2, "medex_id_unverified": None},
    {"query": "ethinylestradiol + levonorgestrel", "atc": "G03AA07", "scope": "contraception", "group": "contraception", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "estrogen avoided in early lactation"},
    # ---- Extension block, added 1 Nov 2026 to bring the list to about 107 resolvable drugs ----
    {"query": "progesterone (vaginal gel)", "atc": None, "scope": "maternal", "group": "pregnancy_support", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "vaginal gel; luteal and preterm-birth use"},
    {"query": "progesterone (vaginal pessary)", "atc": None, "scope": "maternal", "group": "pregnancy_support", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "vaginal pessary"},
    {"query": "phytomenadione (oral)", "atc": None, "scope": "newborn", "group": "newborn_prophylaxis", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "oral form; the injection (885) is already in the list"},
    {"query": "hepatitis B immunoglobulin", "atc": None, "scope": "newborn", "group": "newborn_prophylaxis", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "infants of HBsAg-positive mothers"},
    {"query": "tetanus immunoglobulin", "atc": None, "scope": "maternal", "group": "immunisation", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "tetanus prophylaxis and treatment"},
    {"query": "cabergoline", "atc": None, "scope": "maternal", "group": "lactation", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "lactation suppression; documented warnings"},
    {"query": "drospirenone + ethinylestradiol (0.02 mg)", "atc": None, "scope": "contraception", "group": "contraception", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "combined pill; estrogen avoided in early lactation"},
    {"query": "ethinylestradiol + desogestrel (0.03 mg)", "atc": None, "scope": "contraception", "group": "contraception", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "combined pill; estrogen avoided in early lactation"},
    {"query": "ethinylestradiol + levonorgestrel + ferrous fumarate", "atc": None, "scope": "contraception", "group": "contraception", "role": "caution", "tier": 2, "medex_id_unverified": None, "note": "combined pill with iron; plain levonorgestrel + ethinylestradiol is not in MedEx"},
    {"query": "multivitamins and multiminerals (prenatal)", "atc": None, "scope": "maternal", "group": "supplements", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "pregnancy-specific product; check vitamin A content"},
    {"query": "vitamins and minerals (pregnancy and breast-feeding formula)", "atc": None, "scope": "maternal", "group": "supplements", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "pregnancy-specific product"},
    {"query": "ferrous sulfate + folic acid", "atc": None, "scope": "maternal", "group": "anaemia", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "iron-folate combination"},
    {"query": "ferrous fumarate + folic acid", "atc": None, "scope": "maternal", "group": "anaemia", "role": "core", "tier": 2, "medex_id_unverified": None, "note": "iron-folate combination; single ferrous fumarate is not in MedEx"},
]

# Dropped from the earlier list: dienogest (endometriosis progestin, not an MCH core drug).


def by_tier(tier):
    return [d for d in MCH_SEARCH_LIST if d["tier"] == tier]


def by_role(role):
    return [d for d in MCH_SEARCH_LIST if d["role"] == role]


if __name__ == "__main__":
    import csv, sys
    fields = ["query", "atc", "scope", "group", "role", "tier", "medex_id_unverified", "note"]
    w = csv.DictWriter(sys.stdout, fieldnames=fields)
    w.writeheader()
    for d in MCH_SEARCH_LIST:
        w.writerow({k: d.get(k) for k in fields})
