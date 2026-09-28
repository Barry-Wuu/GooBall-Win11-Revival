Shader "GUI/Outlined Text Shader"
{
	Properties {
		_OutlineTex ("Outline Texture", 2D) = "dummy.jpg" {}
		_TextTex ("Font Texture", 2D) = "dummy.jpg" {}
		_Color ("Outline Color", Color) = (1,1,1,1)
		_TextColor ("Text Color", Color) = (1,1,1,1)
	}
	
	SubShader {
		Lighting Off
		cull off 
		ztest always
		Zwrite off
		Color (0,0,0,.25)
		Fog { Mode Off }
	//	ColorMask RGB
		Tags { "Queue" = "Transparent" }
		Pass {
			Blend SrcAlpha OneMinusSrcAlpha
			SetTexture [_OutlineTex] {
				constantColor [_Color]
				combine constant, texture - constant DOUBLE
			}
		}

		Pass {
			Blend SrcAlpha OneMinusSrcAlpha
			Color [_Color]
			SetTexture [_TextTex] {
				constantColor [_TextColor]
				combine constant, texture - primary DOUBLE
			}
		}
	}
}

/* Experimenting with fadeout support
Shader "GUI/Outlined Text Shader"
{
	Properties {
		_OutlineTex ("Outline Texture", 2D) = "dummy.jpg" {}
		_TextTex ("Font Texture", 2D) = "dummy.jpg" {}
		_OutlineColor ("Outline Color", Color) = (1,1,1,1)
		_TextColor ("Text Color", Color) = (1,1,1,1)
	}
	
	SubShader {
		Lighting Off
		cull off 
		ztest always
		Zwrite off
		Color (0,0,0,.3)
		Fog { Mode Off}
		Pass {
			Blend SrcAlpha OneMinusSrcAlpha
			SetTexture [_OutlineTex] {
				constantColor [_OutlineColor]
				combine constant, texture - constant DOUBLE
			}
			SetTexture [_TextTex] {
				constantColor [_TextColor]
				combine constant lerp (texture) previous, previous * constant
				combine previous, previous - texture DOUBLE
			}
		}
		Pass {
			Blend SrcAlpha OneMinusSrcAlpha
			Color [_OutlineColor]
			SetTexture [_TextTex] {
				constantColor [_TextColor]
				combine constant, texture - primary DOUBLE
			}
		}
	}
}
*/