package com.example.api;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.Map;

@RestController
@RequestMapping("/incident")
public class IncidentController {

    @PostMapping("/approve")
    public Map<String, String> approve(@RequestBody Map<String, String> body) {
        return Map.of(
            "status", "APPROVED",
            "incident", body.get("id")
        );
    }
}
