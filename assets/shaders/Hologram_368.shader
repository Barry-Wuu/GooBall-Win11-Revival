Shader "FX/Hologram projection" {
	Properties {
		_Color ("Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
		_FalloffTex ("Falloff (fresnel(x), dist(y)", 2D) = "" {}
		_FalloffCube ("FalloffCube", CUBE) = "" {}
	}
	SubShader {
		Tags { "Queue" = "Transparent" }
		zwrite off
		ColorMask RGB
		Blend One SrcAlpha
		Fog { Color (0,0,0,0)	}
		LoadProgram "FresnelRays.cgvp"
		Pass { 
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha 
			}
			SetTexture [_FalloffTex] {
				combine texture alpha * previous double, one-  texture alpha * one- previous
			}
		}
	}
	SubShader {
		TexCount 2
		Tags { "Queue" = "Transparent" }
		zwrite off
		ColorMask RGB
		Blend One SrcAlpha
		Fog { Color (0,0,0,0)	}
		Lighting On
		Pass { 
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha 
			}
			SetTexture [_FalloffCube] {
				constantColor [_Color]
				combine previous * ONE - texture alpha DOUBLE, previous * texture alpha
			}
		}
	}
}