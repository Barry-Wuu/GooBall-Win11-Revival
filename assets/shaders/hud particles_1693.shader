Shader "Particles/Pickup Aura"
{
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags {
			"Queue" = "Transparent"
		}
		Fog {
			Color (0,0,0,0)
		}
		Cull Off
		Lighting Off
		zwrite off
		ztest always
		Blend OneMinusDstColor One
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture DOUBLE, constant *  texture DOUBLE
			}
			SetTexture [_MainTex] {
				combine previous * primary, previous * primary
			}
		}
	}
}