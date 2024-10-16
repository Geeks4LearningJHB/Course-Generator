package com.geeks4learning.CourseGen;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CourseGenApplication {

	@Value("${openai.key}") //injects the key from the application.properties file
	private String apiKey;
	public static void main(String[] args) {
		SpringApplication.run(CourseGeneratorApplication.class, args);
	}

	@Bean
	public RestTemplate restTemplate(){
		System.out.println("api: " + apiKey);
		RestTemplate restTemplate = new RestTemplate();
		restTemplate.getInterceptors().add(((request, body, execution) ->{
			request.getHeaders().add("Authorization", "Bearer " + apiKey);
			return execution.execute(request, body);
		}));
		return restTemplate;
	}

}
