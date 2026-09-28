Shader "Particles/LightFlare" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_Offset ("Depth offset", float) = 0
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		cull off
		Lighting Off
		zwrite off
		Blend ONE ONE
		Fog { Mode Off	}
		color (1,1,1,1)
		Offset [_Offset], [_Offset]
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture DOUBLE, constant *  texture DOUBLE
			}
			SetTexture [_MainTex] {
				combine previous * primary, constant
			}
		}
	}
}