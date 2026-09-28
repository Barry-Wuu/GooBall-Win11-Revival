Shader "Particles/AddMult" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Additive texture (RGB)", 2D) = "dummy.jpg"
		_AlphaTex ("Subtractive texture (A)", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		zwrite off
		Blend One OneMinusSrcAlpha
		Fog { Color (0,0,0,0) }
		BindChannels {
			bind "Color", color
			bind "Vertex", vertex
			bind "TexCoord", texcoord0
		}
		ColorMask RGB
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture, one - constant
			}
			SetTexture [_AlphaTex] {
				constantColor (0,0,0,0)
				combine previous * primary, one - primary lerp (texture) constant
			}		
		}
	}
}
