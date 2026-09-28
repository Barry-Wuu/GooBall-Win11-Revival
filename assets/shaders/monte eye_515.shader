Shader "GooBall/monte eye"
{
	Properties {
		_Color ("Color", Color) = (1,1,1,1)
		_Brightness ("Front brightness", range (0,1)) = .5 
		_MainTex ("Reflection Texture", Cube) = "dummy.jpg" {
			TexGen CubeReflect
		}
		_RefractTex ("Refraction Texture", Cube) = "dummy.jpg" {
			TexGen CubeReflect
		}
		_2D ("Reflection Texture 2D", 2D) = "dummy.jpg" {
			TexGen SphereMap
		}
	}
	
	SubShader {
		Lighting Off
		Pass {
//			ColorMask RGB
			SetTexture [_RefractTex] {
				constantColor [_Color]
				combine texture * constant
			}
			SetTexture [_MainTex] {
				constantColor (0,0,0, [_Brightness])
				combine texture * constant + previous
			}
		}
	}
	SubShader {
		Lighting Off
		Pass {
//			ColorMask RGB
			SetTexture [_2D] {
				constantColor [_Color]
				combine texture * constant
			}
			SetTexture [_2D] {
				constantColor (0,0,0, [_Brightness])
				combine texture + previous
			}
		}
	}
}