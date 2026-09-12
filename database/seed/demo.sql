INSERT INTO routes(id,name,geometry) VALUES
('R17','Eastern Express Corridor',ST_GeomFromText('LINESTRING(72.877 19.076,72.889 19.083,72.902 19.091,72.916 19.099)',4326)),
('R24','Western Express Corridor',ST_GeomFromText('LINESTRING(72.864 19.043,72.877 19.076,72.902 19.091,72.929 19.108)',4326)),
('R09','LBS Marg Corridor',ST_GeomFromText('LINESTRING(72.850 19.055,72.865 19.068,72.881 19.080)',4326)),
('R18','Airport Connector',ST_GeomFromText('LINESTRING(72.860 19.090,72.880 19.105,72.910 19.120)',4326)),
('R19','Harbour Link',ST_GeomFromText('LINESTRING(72.900 19.020,72.920 19.040,72.940 19.060)',4326)),
('R20','North Loop',ST_GeomFromText('LINESTRING(72.870 19.110,72.890 19.125,72.915 19.140)',4326)),
('R21','Civic Centre',ST_GeomFromText('LINESTRING(72.845 19.070,72.865 19.080,72.885 19.090)',4326)),
('R22','Coastal Road',ST_GeomFromText('LINESTRING(72.830 19.040,72.850 19.050,72.875 19.060)',4326)),
('R23','Midtown Shuttle',ST_GeomFromText('LINESTRING(72.880 19.060,72.900 19.070,72.920 19.080)',4326))
ON CONFLICT (id) DO NOTHING;
INSERT INTO buses(id,route_id,status,location,last_event_at,events_today) VALUES
('BUS-042','R17','ONLINE',ST_SetSRID(ST_Point(72.877,19.076),4326)::geography,now(),17),('BUS-031','R17','ONLINE',ST_SetSRID(ST_Point(72.87703,19.07603),4326)::geography,now(),14),('BUS-017','R24','ONLINE',ST_SetSRID(ST_Point(72.902,19.091),4326)::geography,now(),23),('BUS-118','R24','ONLINE',ST_SetSRID(ST_Point(72.929,19.108),4326)::geography,now(),12),('BUS-009','R09','ONLINE',ST_SetSRID(ST_Point(72.865,19.068),4326)::geography,now(),19),('BUS-020','R18','ONLINE',ST_SetSRID(ST_Point(72.880,19.105),4326)::geography,now(),11),('BUS-021','R19','ONLINE',ST_SetSRID(ST_Point(72.920,19.040),4326)::geography,now(),10),('BUS-022','R20','ONLINE',ST_SetSRID(ST_Point(72.890,19.125),4326)::geography,now(),9),('BUS-023','R21','ONLINE',ST_SetSRID(ST_Point(72.865,19.080),4326)::geography,now(),8),('BUS-024','R22','ONLINE',ST_SetSRID(ST_Point(72.850,19.050),4326)::geography,now(),8),('BUS-025','R23','ONLINE',ST_SetSRID(ST_Point(72.900,19.070),4326)::geography,now(),7)
ON CONFLICT (id) DO NOTHING;
INSERT INTO road_issues(id,type,severity,confidence,location,status,first_detected_at,last_detected_at,observation_count,buses_observed,severity_reason,route_id) VALUES
('RD-1042','POTHOLE','HIGH',.96,ST_SetSRID(ST_Point(72.877,19.076),4326)::geography,'DETECTED',now()-interval '6 days',now()-interval '2 minutes',17,6,'HIGH severity: high-confidence pothole observed by 6 buses in a high-density corridor.','R17'),
('RD-1038','WATERLOGGING','MEDIUM',.88,ST_SetSRID(ST_Point(72.864,19.043),4326)::geography,'VERIFIED',now()-interval '2 days',now()-interval '1 hour',8,3,'MEDIUM severity: repeated waterlogging observations require maintenance review.','R24'),
('RD-1029','ROAD_DAMAGE','LOW',.72,ST_SetSRID(ST_Point(72.865,19.068),4326)::geography,'REPAIR_VERIFIED',now()-interval '14 days',now()-interval '2 days',5,3,'Repair verification completed after repeated road-damage observations.','R09')
ON CONFLICT (id) DO NOTHING;
INSERT INTO incidents(id,type,vehicle,confidence,location,timestamp,status,evidence_url) VALUES
('INC-0281','VEHICLE_COLLISION','BUS-118',.91,ST_SetSRID(ST_Point(72.929,19.108),4326)::geography,now()-interval '22 minutes','CRITICAL','demo://evidence/incident-0281.jpg'),
('INC-0274','PEDESTRIAN_RISK','BUS-017',.78,ST_SetSRID(ST_Point(72.902,19.091),4326)::geography,now()-interval '2 hours','INVESTIGATING','demo://evidence/incident-0274.jpg')
ON CONFLICT (id) DO NOTHING;
INSERT INTO traffic_measurements(route_id,vehicle_count,vehicle_types,density,average_speed,measured_at) VALUES
('R17',42,'{"car":24,"bus":6,"truck":12}','HIGH',18,now()-interval '20 minutes'),('R24',28,'{"car":20,"bus":5,"truck":3}','MEDIUM',29,now()-interval '45 minutes'),('R09',17,'{"car":12,"bus":3,"truck":2}','LOW',39,now()-interval '2 hours'),('R17',51,'{"car":31,"bus":8,"truck":12}','CRITICAL',14,now()-interval '5 hours');
INSERT INTO maintenance_tasks(id,issue_id,department,status,due_date,notes,created_at,updated_at) VALUES ('WO-DEMO-1042','RD-1042','Municipal Roads Division','DETECTED',CURRENT_DATE+2,'Initial work order created from road-issue workflow.',now()-interval '1 day',now()-interval '1 day') ON CONFLICT (id) DO NOTHING;
INSERT INTO audit_logs(action,user_id,metadata) VALUES ('SEED_DEMO_DATA','demo-authority','{"source":"database/seed/demo.sql"}');
