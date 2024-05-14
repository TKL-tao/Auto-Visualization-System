package datainsights.web.api;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.multipart.MultipartFile;
// import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.io.IOException;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@RestController
public class FileUploadController {
    
    private static String UPLOADED_FOLDER = "D:/Development/datainsights/src/main/java/datainsights/temp/";

    @PostMapping("/upload")
    public String singleFileUpload(@RequestParam("file") MultipartFile file) {

        if (file.isEmpty()) {
            return "Please upload your file";
        }

        File folder = new File(UPLOADED_FOLDER);
        if (folder.isDirectory()) {
            File[] files = folder.listFiles();
            if (files != null && files.length > 0) {
                for (File f : files) {f.delete();}
            }
        }


        try {
            byte[] bytes = file.getBytes();
            Path path = Paths.get(UPLOADED_FOLDER + file.getOriginalFilename());
            Files.write(path, bytes);

            return "File uploading succeeded";
        } catch (IOException e) {
            e.printStackTrace();
        }

        return "File uploading failed";
    }
}
