package datainsights.data;
import org.springframework.data.repository.CrudRepository;

import datainsights.User;

public interface UserRepository extends CrudRepository<User, Long> {

  User findByUsername(String username);
  
}