package datainsights;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import datainsights.data.UserRepository;

@SpringBootApplication
public class DatainsightsApplication {

	public static void main(String[] args) {
		SpringApplication.run(DatainsightsApplication.class, args);
	}

	@Bean
	public CommandLineRunner dataLoader(UserRepository userRepo,
										PasswordEncoder encoder) {
		return new CommandLineRunner() {
			@Override
			public void run(String... args) throws Exception {
				userRepo.save(new User("TKL", encoder.encode("123456"),
							  "Xiaotao Zou", "Duxue_Road", "Guangzhou", "Guangdong", "111", "911"));
			}
		};
	}

}
