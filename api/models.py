from django.db import models

class File(models.Model):
    file = models.FileField(blank=False, null=False)
    
    def __str__(self):
        return self.file.name

class Invoice(models.Model):
  file = models.OneToOneField(File, on_delete= models.CASCADE, primary_key=True)
  num = models.CharField(blank=False, max_length=200)
  dt = models.CharField(blank=False, max_length=200)

  def __str__(self):
      return self.num