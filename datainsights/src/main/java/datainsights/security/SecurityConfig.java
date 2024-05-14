package datainsights.security;

// import java.util.ArrayList;
// import java.util.Arrays;
// import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.core.authority.SimpleGrantedAuthority;
// import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
// import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

import datainsights.User;
import datainsights.data.UserRepository;

@Configuration
public class SecurityConfig {
   
  @Bean
  public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
  }
  
  @Bean
  public UserDetailsService userDetailsService(UserRepository userRepo) {
    return username -> {
      User user = userRepo.findByUsername(username);
      if (user != null) {
        return user;
      }
      throw new UsernameNotFoundException(
                      "User '" + username + "' not found");
    };
  }
  
  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
  
    return http
      .authorizeRequests()
        .mvcMatchers("autovisual").hasRole("USER") //mvcMatchers("autovisual")
        .anyRequest().permitAll()

      .and()
        .formLogin()
          .loginPage("/login")
          .defaultSuccessUrl("/autovisual", true)    

      .and()
       .build();
  }
  
}