

package com.geeks4learning.CourseGen.config;
 
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.OpenAPI;
 
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
 
@Configuration
public class OpenApiConfig {
 
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("CourseGen API")
                        .version("1.0")
                        .description("Application for generating course content using OpenAIs GPTs"));
    }
 
    @Configuration
    public class WebConfig implements WebMvcConfigurer {
 
        @Override
        public void addCorsMappings(CorsRegistry registry) {
            registry.addMapping("/**")
                    .allowedOrigins("http://localhost:8080") // Update with your frontend URL
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                    .allowedHeaders("*");
        }
    }
 
    // @Bean
    // public ModelMapper modelMapper() {
    //     ModelMapper modelMapper = new ModelMapper();
    //     modelMapper.getConfiguration()
    //             .setFieldMatchingEnabled(true)
    //             .setFieldAccessLevel(org.modelmapper.config.Configuration.AccessLevel.PRIVATE);
    //     return modelMapper;
    // }
}
