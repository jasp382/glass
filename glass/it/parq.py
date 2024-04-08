"""
Data to parquet
"""

import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

from glass.rd import tbl_to_obj
from glass.pys.oss import lst_ff, fprop


def xlsx_to_parquet(xlsx, parquet) -> str|None:

    try:
        df = tbl_to_obj(xlsx, fformat='.xlsx')

        if df.empty:
            return None
        
        df.to_parquet(parquet, index=False, engine='pyarrow', compression='snappy')

        return True, parquet
    
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"{xlsx}: {e}\n{tb}"


def xlsxs_to_parquet(in_folder:str, outfolder: str, max_workers: int=max(1, (os.cpu_count() or 4) - 1)):
    """
    Folder with xlsx's to parquet
    """

    t0 = time.time()

    tbls = lst_ff(in_folder, file_format='.xlsx')

    print(f"Encontrados {len(tbls)} ficheiros Excel em {in_folder}")

    ok_count = 0
    fail_count = 0
    errors = []

    with ProcessPoolExecutor(max_workers=max_workers) as ex:

        futures = {
            ex.submit(xlsx_to_parquet, t, os.path.join(
                outfolder, f'{fprop(t, "fn")}.parquet'
            )) : t for t in tbls
        }

        for i, fut in enumerate(as_completed(futures), 1):
            ok, msg = fut.result()

            if ok:
                ok_count += 1
                #print(f"[{i}/{len(futures)}] ✅ {msg}")
            
            else:
                fail_count += 1
                errors.append(msg)
                #print(f"[{i}/{len(futures)}] ❌ ERRO: {msg}")
    
    elapsed = time.time() - t0
    print(f"\nConversão concluída em {elapsed:.1f}s — sucesso: {ok_count}, falhas: {fail_count}")

    if errors:
        err_log = os.path.join(outfolder, "conversion_errors.log")
        with open(err_log, "w", encoding="utf-8") as f:
            for e in errors:
                f.write(e + "\n\n")
        print(f"Erros registados em: {err_log}")
    
    return outfolder

