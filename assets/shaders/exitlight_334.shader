Shader "FX/Exit Gate light" {
	Properties {
		_Color ("Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
		_FalloffTex ("Falloff (fresnel(x), dist(y)", 2D) = "" {}
	}
	SubShader {
		Tags { "Queue" = "Transparent" }
		cull off
		zwrite off
		Blend ONEMinusDstColor ONEMinusSrcAlpha
		Fog { Color (0,0,0,0)	}
		LoadProgram "FresnelRays.cgvp"
		Pass { 
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha 
			}
			SetTexture [_FalloffTex] {
				combine texture alpha * previous double
			}
		}
	}
	SubShader {
		Tags { "Queue" = "Transparent" }
		cull off
		zwrite off
		Blend ONEMinusDstColor ONEMinusSrcAlpha
		Fog { Color (0,0,0,0)	}
		Pass { 
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha 
			}
			SetTexture [_FalloffTex] {
				combine texture alpha * previous double
			}
		}
	}
}  