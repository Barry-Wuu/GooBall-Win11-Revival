Shader "GooBall/MapScreen Dot" {
	Properties {
//		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_Color ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		AlphaTest Greater .1
		ZTest always
		Fog { color (0,0,0,0)	}
		Offset -5, -100
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
		Pass {
			SetTexture [_MainTex] { 
				constantColor [_Color]
				combine constant DOUBLE, constant *  texture DOUBLE
			}
		/*	SetTexture [_MainTex] {
				constantColor [_Color]
				combine previous * primary, texture * constant
			}*/
		}
	}
} 
