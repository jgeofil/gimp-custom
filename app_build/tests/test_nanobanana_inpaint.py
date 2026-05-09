import pytest
import os
from unittest.mock import MagicMock, patch

import gi
gi.require_version("Gimp", "3.0")

# Import the module to test
import nanobanana_inpaint
from nanobanana_inpaint import NanobananaInpaint

# We don't instantiate NanobananaInpaint because it causes a segfault 
# in libgimp-3.0 when run outside of the GIMP process.
# We will just pass None as self to its helper methods.

def test_compute_crop_bounds():
    image = MagicMock()
    image.get_width.return_value = 1000
    image.get_height.return_value = 1000
    
    # 1. Normal crop (well within bounds)
    x0, y0, w, h = NanobananaInpaint._compute_crop_bounds(None, image, 200, 200, 100, 100)
    assert x0 == 150
    assert y0 == 150
    assert w == 200
    assert h == 200

    # 2. Edge crop (near 0)
    x0, y0, w, h = NanobananaInpaint._compute_crop_bounds(None, image, 10, 10, 100, 100)
    assert x0 == 0
    assert y0 == 0
    assert w == 160
    assert h == 160

    # 3. Edge crop (near max)
    x0, y0, w, h = NanobananaInpaint._compute_crop_bounds(None, image, 900, 900, 100, 100)
    assert x0 == 850
    assert y0 == 850
    assert w == 150
    assert h == 150

def test_extract_image_from_response():
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.data = b"image_data"
    
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    
    mock_candidate = MagicMock()
    mock_candidate.content = mock_content
    
    mock_response.candidates = [mock_candidate]
    mock_response.parts = None
    
    assert NanobananaInpaint._extract_image(None, mock_response) == b"image_data"

def test_extract_image_from_parts():
    mock_response = MagicMock()
    mock_response.candidates = []
    
    mock_part = MagicMock()
    mock_part.inline_data.data = b"parts_data"
    
    mock_response.parts = [mock_part]
    
    assert NanobananaInpaint._extract_image(None, mock_response) == b"parts_data"

def test_extract_image_none():
    mock_response = MagicMock()
    mock_response.candidates = []
    mock_response.parts = []
    
    assert NanobananaInpaint._extract_image(None, mock_response) is None

@patch("time.sleep")
@patch("nanobanana_inpaint.Gimp.message")
@patch("nanobanana_inpaint.Gimp.progress_set_text")
def test_api_call_with_retry_success_first_try(mock_prog, mock_msg, mock_sleep):
    client = MagicMock()
    client.models.generate_content.return_value = "success"
    
    res = NanobananaInpaint._api_call_with_retry(None, client, "model", [], None)
    assert res == "success"
    assert client.models.generate_content.call_count == 1
    mock_sleep.assert_not_called()

@patch("time.sleep")
@patch("nanobanana_inpaint.Gimp.message")
@patch("nanobanana_inpaint.Gimp.progress_set_text")
def test_api_call_with_retry_transient_error(mock_prog, mock_msg, mock_sleep):
    client = MagicMock()
    client.models.generate_content.side_effect = [
        Exception("API Error 429 Too Many Requests"),
        Exception("API Error 503 Service Unavailable"),
        "success"
    ]
    
    res = NanobananaInpaint._api_call_with_retry(None, client, "model", [], None)
    assert res == "success"
    assert client.models.generate_content.call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(2)
    mock_sleep.assert_any_call(4)

@patch("time.sleep")
@patch("nanobanana_inpaint.Gimp.message")
@patch("nanobanana_inpaint.Gimp.progress_set_text")
def test_api_call_with_retry_permanent_error(mock_prog, mock_msg, mock_sleep):
    client = MagicMock()
    client.models.generate_content.side_effect = Exception("API Error 400 Bad Request")
    
    with pytest.raises(Exception, match="400"):
        NanobananaInpaint._api_call_with_retry(None, client, "model", [], None)
    
    assert client.models.generate_content.call_count == 1
    mock_sleep.assert_not_called()

@patch("nanobanana_inpaint.tempfile.gettempdir")
@patch("nanobanana_inpaint.os.remove")
@patch("nanobanana_inpaint.Gimp.file_save")
def test_export_image_png(mock_file_save, mock_remove, mock_tempdir):
    mock_tempdir.return_value = "/tmp"
    
    image = MagicMock()
    dup = MagicMock()
    image.duplicate.return_value = dup
    dup.get_width.return_value = 1000
    dup.get_height.return_value = 1000
    
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b"png_data"
        
        data, mime = NanobananaInpaint._export_image(None, image)
        
        dup.flatten.assert_called_once()
        dup.crop.assert_not_called()
        dup.delete.assert_called_once()
        mock_file_save.assert_called_once()
        
        assert data == b"png_data"
        assert mime == "image/png"

@patch("nanobanana_inpaint.tempfile.gettempdir")
@patch("nanobanana_inpaint.os.remove")
@patch("nanobanana_inpaint.Gimp.file_save")
def test_export_image_jpeg(mock_file_save, mock_remove, mock_tempdir):
    mock_tempdir.return_value = "/tmp"
    
    image = MagicMock()
    dup = MagicMock()
    image.duplicate.return_value = dup
    dup.get_width.return_value = 2000
    dup.get_height.return_value = 2000
    # 4,000,000 > JPEG_THRESHOLD_PIXELS (which is ~1,398,101)
    
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b"jpeg_data"
        
        data, mime = NanobananaInpaint._export_image(None, image)
        
        assert data == b"jpeg_data"
        assert mime == "image/jpeg"

@patch("nanobanana_inpaint.tempfile.gettempdir")
@patch("nanobanana_inpaint.os.remove")
@patch("nanobanana_inpaint.Gimp.file_save")
def test_export_mask(mock_file_save, mock_remove, mock_tempdir):
    mock_tempdir.return_value = "/tmp"
    
    image = MagicMock()
    sel_channel = MagicMock()
    image.get_selection.return_value = sel_channel
    image.get_width.return_value = 500
    image.get_height.return_value = 500
    
    with patch("nanobanana_inpaint.Gimp.Image.new") as mock_img_new:
        mask_img = MagicMock()
        mock_img_new.return_value = mask_img
        
        with patch("nanobanana_inpaint.Gimp.Layer.new_from_drawable") as mock_layer_new:
            mask_layer = MagicMock()
            mock_layer_new.return_value = mask_layer
            
            with patch("builtins.open", new_callable=MagicMock) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = b"mask_data"
                
                data = NanobananaInpaint._export_mask(None, image, crop_bounds=(10, 20, 100, 200))
                
                mock_img_new.assert_called_with(500, 500, nanobanana_inpaint.Gimp.ImageBaseType.GRAY)
                mask_img.insert_layer.assert_called_once_with(mask_layer, None, 0)
                mask_img.crop.assert_called_once_with(100, 200, 10, 20)
                mask_img.delete.assert_called_once()
                mock_file_save.assert_called_once()
                
                assert data == b"mask_data"
