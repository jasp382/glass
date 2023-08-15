import { NgModule } from "@angular/core";
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// FireLoc Modules
import { FeatModule } from "src/app/feat/feat.module";

// Fort Awesome
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";

// Bootstrap
import { NgbModule } from "@ng-bootstrap/ng-bootstrap";

// Components
import { GraphsComponent } from "./graphs/graphs.component";
import { LayersComponent } from "./layers/layers.component";
import { LegendComponent } from "./legend/legend.component";

/**
 * Backoffice Map Module. Contains components in the Backoffice with datasets related to the Geoportal map.
 */
@NgModule({
    declarations: [GraphsComponent, LayersComponent, LegendComponent],
    imports: [
        CommonModule,
        FeatModule,
        FontAwesomeModule,
        FormsModule,
        ReactiveFormsModule,
        NgbModule
    ],
    exports: [
        GraphsComponent,
        LayersComponent,
        LegendComponent
    ]
})
export class MapModule { }