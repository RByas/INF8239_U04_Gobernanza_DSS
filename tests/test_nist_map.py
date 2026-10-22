import pandas as pd, pytest
from inf8239_u04.governance import validate_rmf_map
def test_student_rmf_map_is_traceable():
    assert validate_rmf_map(pd.read_csv("student_inputs/nist_rmf_map.csv"))
def test_rmf_map_rejects_missing_evidence():
    df=pd.DataFrame([{"function":f,"subcategory":f"{f} 1.1","requirement":"x","control":"x","evidence":"no/existe.md","status":"verificado","risk_ids":"R01"} for f in ("GOVERN","MAP","MEASURE","MANAGE")])
    with pytest.raises(ValueError,match="Evidence not found"): validate_rmf_map(df)
