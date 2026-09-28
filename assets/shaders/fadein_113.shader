// Standard openGL single-texture diffuse shader

// Written by Nicholas Francis. Copyright OTE 2003

SHADER "RenderFX/FadeIn" { 
    	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
//		_MainTex ("Main Texture", 2d) = "wood0.jpg"
	}
	
	SUBSHADER {
		Pass {
//			Blend DstColor SrcColor
			Blend SrcAlpha OneMinusSrcAlpha
			ZTest Always
			ZWrite Off
			Color [_Color]
			Cull Off
        			Lighting Off					// Enable standard OpenGL lighting
	        }   
	}
}