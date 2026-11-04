# P1 MedEx pilot report

Date: 28 Oct 2026 · Author: Claude (research support) for Shariat Shojoy
Data: 8 saved MedEx pages (4 drugs × English and Bangla) plus 1 pasted Bangla page (oxytocin). Files saved on 28 Oct 2026.
Status: provisional. Based on 5 drugs. Differences were found by comparing the English and Bangla texts; none has been clinician-verified yet.

## 1. Result in one paragraph

MedEx has real Bangla body text for almost every section, including pregnancy and lactation for 4 of 5 pilot drugs. But the Bangla is a lossy and inconsistent translation of the English. We found errors that change meaning, including three in a single magnesium sulfate page. Decision: **GO, with a changed role for the Bangla.** English is the fact backbone; the Bangla pages are Bangla evidence and a subject of study, never the only source of a safety fact.

## 2. ID verification (resolve by name, not by ID)

| Drug | ID in your list | ID on the page | Result |
|---|---|---|---|
| oxytocin | 854 | 854 | match |
| misoprostol | 764 | 764 | match |
| labetalol hydrochloride | 1821 | 1821 | match |
| magnesium sulfate | 713 | **1551** | **mismatch** |
| warfarin sodium | 1119 | **1166** | **mismatch** |

2 of 5 IDs were wrong. Treat the other 37 unverified IDs in the search list as unreliable until each page is opened and the name checked.

## 3. Section coverage (accordion sections)

| Drug | English | Bangla | In English but not in Bangla |
|---|---|---|---|
| oxytocin | 15 (from a summary only) | 11 | Pharmacology, Interaction, Pregnancy & Lactation |
| misoprostol | 12 | 12 | none |
| magnesium sulfate | 13 | 11 | Composition, Description |
| labetalol | 11 | 11 | none |
| warfarin | 12 | 11 | Pharmacology (Bangla has a Description section instead) |

- **Therapeutic Class** is always a Bangla heading over an English value ("bangla_label_only").
- **Available Brand Names** sits outside the accordion and is in English on both language pages.
- The sections align one to one by position, so a clean parallel Bangla–English corpus is possible.
- Pregnancy & Lactation and Interaction exist in Bangla for misoprostol, magnesium sulfate, labetalol and warfarin; only oxytocin's Bangla page lacks them.

## 4. Fidelity findings (English vs Bangla)

| # | Drug, section | English | Bangla | Why it matters |
|---|---|---|---|---|
| 1 | magnesium sulfate, Indications | "hypo**magnesaemia**" | "হাইপারম্যাগনেসেমিয়া" (hyper-) | Opposite condition |
| 2 | magnesium sulfate, Indications | seizures of "acute uremia, hypothyroidism and **eclampsia**" | "খিচুনি প্রতিরোধ ও নিয়ন্ত্রণ" (seizure prevention); eclampsia is not mentioned anywhere on the Bangla page | The main MCH use of the drug is missing in Bangla |
| 3 | magnesium sulfate, Indications | "may be used as a **laxative**" | "রোচক ঔষধ" (রোচক normally means appetising; laxative is রেচক) | One-vowel change, different meaning |
| 4 | magnesium sulfate, Contraindications | "significantly **decreased** kidney function" | "কিডনীর স্বাভাবিক ক্রিয়াতে প্রতিনির্দেশিত" (contraindicated in **normal** kidney function, as written) | Can be read as inverted |
| 5 | magnesium sulfate, Indications | anticonvulsant "when administered **parenterally**" | "মাংসপেশীতে" (intramuscularly) | Route narrowed |
| 6 | misoprostol, Pregnancy & Lactation | "**not recommended** for nursing mothers" | "প্রযোজ্য নয়" (not applicable) | Recommendation strength blurred |
| 7 | misoprostol, Pregnancy & Lactation | "**potential** for serious adverse reactions in nursing infants" | "ঘটাতে পারে" in newborns | Possible risk becomes stated risk; infants narrowed to newborns |
| 8 | misoprostol, Pregnancy & Lactation | contraindicated "because of the abortifacient property" | reason absent | Explanation lost |
| 9 | misoprostol, Pregnancy & Lactation | warning includes "danger to other women of childbearing potential if taken by mistake" | not included | Counselling warning dropped |
| 10 | misoprostol, Pregnancy & Lactation | test "**within** 2 weeks prior" | "২ সপ্তাহ আগে" (2 weeks before) | Timing reading changes |
| 11 | labetalol, Contraindications | "contraindicated" in asthma | "**সম্পূর্ণ** নিষিদ্ধ" (completely prohibited) | Absoluteness added |
| 12 | labetalol, Pregnancy & Lactation | "teratogenic studies"; "no reproducible evidence" | "প্রজনন গবেষণা" (reproduction studies); "কোনো সুনির্দিষ্ট প্রমাণ" (no specific evidence) | Small shifts |

Warfarin's pregnancy and contraindication sections are faithful in meaning, which shows the quality varies by drug.

Other observations:
- **Translation style varies by page.** Labetalol's Bangla is fluent, has Bangla medical terms (হাঁপানি) and 21 English glosses in parentheses. Misoprostol, magnesium sulfate and warfarin are older-style: transliteration-heavy, typos, spelling variants (গ্যাস্ট্রিক, গ্যান্ত্রিক, গ্যাট্রিক, গাষ্ট্রিক on one page; মাগনেসিয়াম and ম্যাগনেসিয়াম in one paragraph). This is a hypothesis to test across 100+ drugs, not yet a result.
- **MedEx's English pregnancy sections are not always clinically complete.** Magnesium sulfate's says only "caution" and never mentions eclampsia, its main obstetric use. Labetalol's gives animal data and "caution" and does not say it is a first-line antihypertensive in pregnancy. MedEx alone cannot ground "preferred in pregnancy" claims, so external validation (P8) is essential.
- **Context-dependent contraindication.** Misoprostol is both indicated (labour induction, PPH) and contraindicated in pregnancy (ulcer use). The schema needs an indication-context qualifier.

## 5. Parser lessons for P2

1. Normalise all Bangla text to Unicode NFC. Headings store য় as one character (U+09DF); typed text may use two.
2. Section containers are `.ac-header` / `.ac-body`; headings and bodies pair by position.
3. Some English bodies contain a truncated copy followed by "... Read more" and the full text. Keep only the text after "... Read more".
4. List items run together in plain text (warfarin contraindications). Parse `<li>` elements separately.
5. Normalise Bangla digits (১-৫) and spelling variants for entity matching.
6. Match each Bangla heading to its English heading by a fixed map, not by position (the two pages can differ by a section).

## 6. Gate decision

Proposed gate: "GO if the safety-critical sections (contraindications, pregnancy and lactation, indications) have real Bangla body text for the pilot drugs."
- Met for misoprostol, magnesium sulfate, labetalol, warfarin (4 of 5). Not met for oxytocin's pregnancy section.
- **GO**, with these changes to the plan:
  1. English is the fact backbone; Bangla is evidence and phrasing only.
  2. Add the translation-fidelity audit as a formal result (error taxonomy, rate per section, per drug).
  3. Add a recommendation-strength field and an indication-context qualifier to the schema (P4).
  4. Resolve MedEx pages by name, then verify.

## 7. Still open

- Oxytocin: only the Bangla paste and a summary of the English page; the saved `/en` and `/bn` HTML files are missing.
- robots.txt was not checked (the fetch tool cannot reach it). Please open `https://medex.com.bd/robots.txt` and paste it.
- Permission email to Ology Limited: not yet sent.
- A clinician has not yet reviewed any difference listed above. Items 1 to 5 should be reviewed first.
