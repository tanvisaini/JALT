from unittest.mock import patch
import data.form as fm


def test_get_form():
    form_data = fm.get_form()
    assert isinstance(form_data, list)
    assert len(form_data) > 0
    for field in form_data:
        assert fm.FLD_NM in field
        assert isinstance(field[fm.FLD_NM], str)
        assert len(field[fm.FLD_NM]) > 0


def test_get_form_descr():
    assert isinstance(fm.get_form_descr(), dict)


def test_get_fld_names():
    field_names = fm.get_fld_names()
    assert isinstance(field_names, list)
    assert len(field_names) > 0
    for name in field_names:
        assert isinstance(name, str)
        assert len(name) > 0