import re
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InfrastructureReport(models.Model):
    CATEGORY_CHOICES = [
        ('Road Damage', 'Road Damage'),
        ('Excessive Flooding', 'Excessive Flooding'),
        ('Landslide', 'Landslide'),
        ('Faded Pavement Markings', 'Faded Pavement Markings'),
        ('Clogged Drainage', 'Clogged Drainage'),
        ('Long-standing Unfinished Construction', 'Long-standing Unfinished Construction'),
        ('Neglected / Broken Infrastructure', 'Neglected / Broken Infrastructure'),
        ('Fallen Tree Obstruction', 'Fallen Tree Obstruction'),
        ('Improper Garbage Dump Sites', 'Improper Garbage Dump Sites'),
        ('Defective Street Lights', 'Defective Street Lights'),
        ('Electrical Grid Unreliability', 'Electrical Grid Unreliability'),
        ('Defective Traffic Lights', 'Defective Traffic Lights'),
    ]
    
    STATUS_CHOICES = [
        ('Reported', 'Reported'),
        ('Verified', 'Verified'),
        ('Dispatched', 'Dispatched'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Flagged', 'Flagged'),
    ]

    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Minor'),
        (3, 'Medium'),
        (4, 'High'),
        (5, 'Critical'),
    ]

    title = models.CharField(max_length=200, blank=True) # Awtomatikong mase-set mula sa category
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3)
    barangay = models.CharField(max_length=100)
    latitude = models.FloatField(default=13.7565)
    longitude = models.FloatField(default=121.0583)
    description = models.TextField()
    photo = models.ImageField(upload_to='reports/', blank=True, null=True)

    landmark = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Reported')
    support_votes = models.IntegerField(default=0)
    priority_score = models.IntegerField(default=0, editable=False)
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        if self.category and not self.title:
            self.title = self.category

        if self.description:
            text = self.description.lower()

            def has_any(keywords):
                return any(kw in text for kw in keywords)

            kw_flooding = ['flood', 'baha', 'overflow', 'submerged', 'tubig', 'lubog', 'umaapaw', 'tulay', 'maulan', 'apaw', 'malunod', 'rumaragasang', 'lampas', 'ilog', 'ulan', 'bagyo', 'krisis', 'lason', 'kailaliman', 'drainage']
            kw_road = ['pothole', 'road', 'bako', 'pit', 'asphalt', 'crack', 'lubak', 'kalsada', 'bitak', 'hukay', 'butas', 'pagsalubak', 'daan', 'palay', 'masubsob', 'nahulog', 'gumuho', 'aksidente', 'sasakyan', 'motor', 'tulay']
            kw_drainage = ['drainage', 'canal', 'clog', 'bara', 'sewer', 'kanal', 'barado', 'imburnal', 'baho', 'lamok', 'dengue', 'bagyo', 'ipis', 'maruming', 'estero', 'basura', 'amoy', 'bacteria', 'sakit']
            kw_lights = ['light', 'post', 'bundi', 'dilim', 'ilaw', 'poste', 'pundido', 'madilim', 'patay', 'yumaong', 'kalyeng', 'takot', 'gabi', 'magnanakaw', 'banta', 'panganib', 'sirang', 'bombilya', 'kuryente', 'pasilidad']
            kw_garbage = ['garbage', 'trash', 'tapon', 'kalat', 'dump', 'basura', 'tambak', 'buidok', 'ipis', 'insekto', 'nakaimbak', 'kanto', 'amoy', 'mabaho', 'langaw', 'piyesta', 'koleksyon', 'plastic', 'latak', 'pabaya']
            kw_landslide = ['landslide', 'erosion', 'guho', 'lupa', 'collapse', 'pagguho', 'bundok', 'liblib', 'panganib', 'bato', 'putik', 'delikado', 'pagbagsak', 'sapa', 'gilid', 'bunduking', 'trahedya', 'sakuna', 'bitak']
            kw_tree = ['tree', 'puno', 'fallen', 'branch', 'dahon', 'sanga', 'nabuwal', 'natumba', 'sampayan', 'acacia', 'hangin', 'harang', 'kawad', 'ugat', 'balagbag', 'sagabal', 'putol', 'daanan']
            kw_construction = ['construction', 'unfinished', 'abandoned', 'projects', 'karatula', 'signboard', 'proyekto', 'center', 'contractor', 'tiwangwang', 'matagal', 'taon', 'buwan', 'tigil', 'pondo', 'korapsyon', 'atraso', 'pangako', 'hilaw', 'gusali']
            kw_pavement = ['pavement', 'marking', 'linya', 'faded', 'bura', 'pedestrian', 'pudpod', 'tawiran', 'tawid', 'kulay', 'putol', 'aspalto', 'tanda', 'guhit', 'blangko', 'bulag', 'dilaw']
            kw_traffic = ['traffic', 'signal', 'pulong', 'pula', 'dilaw', 'green', 'stuck', 'timer', 'batman', 'andar', 'patay', 'sira', 'bungo', 'salubong', 'kawalan', 'intersection', 'hinto', 'sabay', 'sistema']
            kw_electrical = ['electrical', 'grid', 'power', 'brownout', 'kuryente', 'transformer', 'fluctuation', 'plaza', 'hide', 'seek', 'spark', 'sabog', 'kawad', 'saksak', 'voltage', 'disgrasya']
            kw_infrastructure = ['broken', 'neglected', 'infrastructure', 'sira', 'pundasyon', 'shed', 'lumot', 'wasak', 'luma', 'tagas', 'bulok', 'kahoy', 'bakal', 'bubong', 'sahig', 'dingding', 'abandonado', 'pasilidad']

            if not self.category or self.category == 'Neglected / Broken Infrastructure':
                if has_any(kw_flooding):
                    self.category = 'Excessive Flooding'
                elif has_any(kw_road):
                    self.category = 'Road Damage'
                elif has_any(kw_drainage):
                    self.category = 'Clogged Drainage'
                elif has_any(kw_lights):
                    self.category = 'Defective Street Lights'
                elif has_any(kw_garbage):
                    self.category = 'Improper Garbage Dump Sites'
                elif has_any(kw_landslide):
                    self.category = 'Landslide'
                elif has_any(kw_tree):
                    self.category = 'Fallen Tree Obstruction'
                elif has_any(kw_construction):
                    self.category = 'Long-standing Unfinished Construction'
                elif has_any(kw_pavement):
                    self.category = 'Faded Pavement Markings'
                elif has_any(kw_traffic):
                    self.category = 'Defective Traffic Lights'
                elif has_any(kw_electrical):
                    self.category = 'Electrical Grid Unreliability'
                else:
                    self.category = 'Neglected / Broken Infrastructure'
                
                self.title = self.category

            # Automated Severity Scoring Logic
            if not self.severity or self.severity == 3:
                if has_any(['deadly', 'fatal', 'namatay', 'emergency', 'panganib', 'collapsed', 'wasak', 'rumaragasang', 'lampas', 'sumabog', 'nahulog', 'masubsob', 'gumuho']):
                    self.severity = 5
                elif has_any(['deep', 'malalim', 'severe', 'major', 'malaking', 'baradong-barado', 'anlala', 'isang taon na', 'tatlong taon', 'tulay']):
                    self.severity = 4
                elif has_any(['faded', 'light', 'kaunti', 'bahagya', 'asking lang']):
                    self.severity = 1
                else:
                    self.severity = 3

        self.priority_score = (int(self.severity) * 20) + (int(self.support_votes) * 5)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.barangay}) - Score: {self.priority_score}"

    @property
    def next_status(self):
        status_sequence = ['Reported', 'Verified', 'Dispatched', 'In Progress', 'Resolved']
        try:
            idx = status_sequence.index(self.status)
            if idx < len(status_sequence) - 1:
                return status_sequence[idx + 1]
        except ValueError:
            pass
        return None

    @property
    def prev_status(self):
        status_sequence = ['Reported', 'Verified', 'Dispatched', 'In Progress', 'Resolved']
        try:
            idx = status_sequence.index(self.status)
            if idx > 0:
                return status_sequence[idx - 1]
        except ValueError:
            pass
        return None