Shader "Particles/LightFlare NoZTest" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		cull off
		Lighting Off
		ztest Always
		zwrite off
		Blend ONE ONE
		Fog { Mode Off	}
		color (1,1,1,1)
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture alpha DOUBLE, constant *  texture DOUBLE
			}
			SetTexture [_MainTex] {
				constantColor [_TintColor]		
				combine previous * primary, previous
			}
		}
	}
}