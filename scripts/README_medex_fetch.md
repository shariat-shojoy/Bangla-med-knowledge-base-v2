# medex_fetch.py: how to run (BanglaMed P2)

Put `medex_fetch.py` and `medex_mch_search_list.py` in the same folder. Install once:

    pip install requests beautifulsoup4

Use your own email after `--contact` (it goes in the User-Agent so MedEx can reach you).

## Run in steps, and look at each result before the next step

1. Smoke test (about 10 seconds): reads robots.txt and 2 listing pages only.

       python medex_fetch.py --stage index --max-pages 2 --contact you@example.com --out medex_out

   Check that `medex_out/robots.txt` exists and `medex_out/index/generics_index.csv` has about 40 rows.
   Please send me `robots.txt`.

2. Full index (about 84 pages, roughly 4 to 5 minutes at 2.5 s per request):

       python medex_fetch.py --stage index --contact you@example.com --out medex_out

3. Resolve names to MedEx pages (no network). The 20-drug audit list:

       python medex_fetch.py --stage resolve --out medex_out --names "oxytocin,misoprostol,magnesium sulfate,labetalol,warfarin,methylergometrine,tranexamic acid,calcium gluconate,methyldopa,nifedipine,betamethasone,folic acid,ferrous sulfate,gentamicin,paracetamol,captopril,methotrexate,sodium valproate,doxycycline,terbutaline"

   Open `medex_out/resolve_log.csv`:
   - `resolved`: fine.
   - `ambiguous` or `none`: nothing was guessed. Look at the `candidates` column, then create `overrides.csv`:

         query,id
         doxycycline,1234

   - Also check the line "ID differs from the remembered list ID", which lists drugs whose real ID is not the one in the old list.

4. Fetch the English and Bangla pages (about 2 pages per drug, about 3 s each):

       python medex_fetch.py --stage fetch --contact you@example.com --out medex_out --names "<same list as step 3>" --overrides overrides.csv

   Pages already saved are skipped. Add `--with-brands` to also save each generic's brand-names page.

5. Parse (no network):

       python medex_fetch.py --stage parse --out medex_out

   Outputs: `sections.jsonl` (one line per section, with language status) and `parse_qc.csv`.
   Send me `resolve_log.csv`, `manifest.jsonl`, `parse_qc.csv` and the `raw` folder (zip it).

Everything else in `medex_out/`:
- `index/` the saved listing pages and `generics_index.csv`
- `raw/` every page exactly as downloaded
- `manifest.jsonl` URL, time, status and sha256 of each download
- `robots.txt` what the site allowed when you ran it

## Notes
- The tool stops if robots.txt returns anything other than 200 or 404.
- Only allopathic generics are indexed (`/generics`). Herbal ones are `/generics?herbal=1` and are not included.
- If a step fails, send me the printed message. Do not re-run in a loop.
