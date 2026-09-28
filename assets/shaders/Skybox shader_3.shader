Shader "RenderFX/Skybox" {
	Properties {
		_Tint ("Tint Color", Color) = (.5, .5, .5, .5)
		_FrontTex ("Front (+z)", 2D) = "clouds.jpg"
		_BackTex ("Back (-z)", 2D) = "dummy.jpg"
		_LeftTex ("Left (+x)", 2D) = "dummy.jpg"
		_RightTex ("Right (-x)", 2D) = "dummy.jpg"
		_UpTex ("Up (+y)", 2D) = "dummy.jpg"
		_DownTex ("down (-y)", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Cull Off
		ZWrite On
		ZTest Always
		Fog {
			Mode Off
		}
		Lighting Off		
		Color [_Tint]
		Pass {
			SetTexture [_FrontTex] {
				combine texture +- primary, primary
			}
		}
		Pass {
			SetTexture [_BackTex] {
				combine texture +- primary, primary
			}
		}
		Pass {
			SetTexture [_LeftTex] {
				combine texture +- primary, primary
			}
		}
		Pass {
			SetTexture [_RightTex] {
				combine texture +- primary, primary
			}
		}
		Pass {
			SetTexture [_UpTex] {
				combine texture +- primary, primary
			}
		}
		Pass {
			SetTexture [_DownTex] {
				combine texture +- primary, primary
			}
		}
	}
}