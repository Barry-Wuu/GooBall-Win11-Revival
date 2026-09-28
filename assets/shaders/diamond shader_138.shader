Shader "GooBall/diamond"
{
	Properties {
		_Color ("Color", Color) = (1,1,1,1)
		_MainTex ("Reflection Texture", Cube) = "dummy.jpg" {
			TexGen CubeReflect
		}
		_RefractTex ("Refraction Texture", Cube) = "dummy.jpg" {
			Cube
			TexGen CubeReflect
		}
		_2D ("Reflection Texture", 2D) = "dummy.jpg" {
			TexGen SphereMap
		}
	}	
	SubShader {
		Lighting On
		Pass {
			Color (0,0,0,0)
			Cull Front
			SetTexture [_RefractTex] {
				constantColor [_Color]
				combine texture * constant, primary
			}
			SetTexture [_MainTex] {
				combine previous, previous +- texture
			}
		}
		Pass {
			Fog { Color (0,0,0,0)}
			Blend One One
			SetTexture [_RefractTex] {
				constantColor [_Color]
				combine texture * constant
			}
			SetTexture [_MainTex] {
				combine texture + previous, previous +- texture
			}
		}
	}
	SubShader {
		Lighting Off
		Pass {
			SetTexture [_2D] {
				constantColor [_Color]
				combine texture * constant
			}
		}
	}
}
