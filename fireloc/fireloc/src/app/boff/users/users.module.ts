// Modules
import { NgModule } from "@angular/core";
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

// FireLoc Modules
import { FeatModule } from "src/app/feat/feat.module";

// Style
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { NgbModule } from "@ng-bootstrap/ng-bootstrap";

// Components
import { GroupsComponent } from "./groups/groups.component";
import { UsersComponent } from "./users/users.component";

/**
 * Backoffice Users Module. Contains components in the Backoffice with date related to FireLoc users.
 */
@NgModule({
    declarations: [GroupsComponent, UsersComponent],
    imports: [
        CommonModule,
        FeatModule,
        FontAwesomeModule,
        NgbModule,
        FormsModule,
        ReactiveFormsModule,
    ],
    exports: [GroupsComponent, UsersComponent,]
})
export class UsersModule { }