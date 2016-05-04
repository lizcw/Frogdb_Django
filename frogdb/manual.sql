BEGIN;
--
-- Create model Transporter
--
CREATE TABLE "frogs_transporter" ("id" serial NOT NULL PRIMARY KEY, "user_id" integer NOT NULL UNIQUE);
--
-- Alter field disposal_sentby on experiment
--
ALTER TABLE "frogs_experiment" RENAME COLUMN "disposal_sentby" TO "disposal_sentby_id";
ALTER TABLE "frogs_experiment" ALTER COLUMN "disposal_sentby_id" TYPE integer USING "disposal_sentby_id"::integer;
CREATE INDEX "frogs_experiment_disposal_sentby_id_3816db4d_uniq" ON "frogs_experiment" ("disposal_sentby_id");
ALTER TABLE "frogs_experiment" ADD CONSTRAINT "frogs_exper_disposal_sentby_id_3816db4d_fk_frogs_transporter_id" FOREIGN KEY ("disposal_sentby_id") REFERENCES "frogs_transporter" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Alter field death on frog
--
ALTER TABLE "frogs_frog" DROP CONSTRAINT "frogs_frog_death_id_410d2450_fk_frogs_deathtype_id";
ALTER TABLE "frogs_frog" ALTER COLUMN "death_id" DROP NOT NULL;
ALTER TABLE "frogs_frog" ADD CONSTRAINT "frogs_frog_death_id_410d2450_fk_frogs_deathtype_id" FOREIGN KEY ("death_id") REFERENCES "frogs_deathtype" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Alter field transporter on transfer
--
ALTER TABLE "frogs_transfer" RENAME COLUMN "transporter" TO "transporter_id";
ALTER TABLE "frogs_transfer" ALTER COLUMN "transporter_id" TYPE integer USING "transporter_id"::integer;
CREATE INDEX "frogs_transfer_transporter_id_340d0d31_uniq" ON "frogs_transfer" ("transporter_id");
ALTER TABLE "frogs_transfer" ADD CONSTRAINT "frogs_transfer_transporter_id_340d0d31_fk_frogs_transporter_id" FOREIGN KEY ("transporter_id") REFERENCES "frogs_transporter" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "frogs_transporter" ADD CONSTRAINT "frogs_transporter_user_id_9ef71655_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

COMMIT;
