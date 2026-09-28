Shader "GUI/Helpsystem Text Shader"
{
	Properties {
		_TextTex ("Font Texture", 2D) = "dummy.jpg" {}
		_TextColor ("Text Color", Color) = (1,1,1,1)
	}
	
	SubShader {
		Lighting Off
		cull off
		ztest always
		Zwrite off
		Fog { Mode Off }
		Tags {"Queue" = "Transparent" }
		Pass {
			Blend SrcAlpha OneMinusSrcAlpha
			SetTexture [_TextTex] {
				constantColor [_TextColor]
				combine constant, texture * constant
			}
		}
	}
}