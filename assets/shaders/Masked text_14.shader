Shader "GUI/Normal Text Shader"
{
	Properties {
		_TextTex ("Font Texture (A)", 2D) = "dummy.jpg" {}
		_MaskTex ("Mask Texture (A)", 2D) = "dummy.jpg" {}
		_TextColor ("Text Color", Color) = (1,1,1,1)
	}
	
	SubShader {
		Lighting Off
		cull off
		ztest always
		Zwrite off
//		Tags { "Queue" = "Transparent" }
		Pass {
//			AlphaTest Greater 0.3
			Blend SrcAlpha OneMinusSrcAlpha
			SetTexture [_TextTex] {
				constantColor [_TextColor]
				combine constant, texture * constant
			}
			SetTexture [_MaskTex] {
				combine previous, texture * previous
			}
		}
	}
}