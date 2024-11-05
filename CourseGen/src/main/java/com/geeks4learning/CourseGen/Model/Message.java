package com.geeks4learning.CourseGen.Model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class Message {

    private String Message;
    private String Response;

    public void setResponse(String success) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    public void setMessage(String authentication_successful) {
        
    }

    

}
