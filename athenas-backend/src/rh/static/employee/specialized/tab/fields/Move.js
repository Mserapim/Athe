rh.employee.specialized.tab.fields.Move = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Move.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Move.superclass.observerEmployeePk.call(this, {});
            this.getWorkplaceFieldSet().collapse(false);
            this.getWorkassignmentFieldSet().collapse(false);
            this.getConcessionFieldSet().collapse(false);
            this.getStabilizationFieldSet().collapse(false);
            this.getProgressionFieldSet().collapse(false);
            this.getLegalframingFieldSet().collapse(false);
            this.getRedistributionFieldSet().collapse(false);
            // this.getRequisitionFieldSet().collapse(false);
            this.getRemovalFieldSet().collapse(false);
            this.getDiligenceFieldSet().collapse(false);
            this.getAuxCoordenationFieldSet().collapse(false);
            this.getTeletrabalhoFieldSet().collapse(false);
            
        },

        fields: function(cfg){
            var items = [
                this.getWorkplaceFieldSet(),
                this.getWorkassignmentFieldSet(),
                this.getConcessionFieldSet(),
                this.getStabilizationFieldSet(),
                this.getProgressionFieldSet(),
                this.getLegalframingFieldSet(),
                this.getRedistributionFieldSet(),
                // this.getRequisitionFieldSet(),
                this.getRemovalFieldSet(),
                this.getDiligenceFieldSet(),
                this.getAuxCoordenationFieldSet(),
                this.getTeletrabalhoFieldSet(),
            ];
            return items;
        },

        getWorkplaceFieldSet: function(){
            if(!this._workplaceFieldSet)
                this._workplaceFieldSet = this._factoryFieldSet({title: 'Lotação', items:[this.getWorkplace()], height: 350}, this.getWorkplace());
            return this._workplaceFieldSet;
        },

        getWorkassignmentFieldSet: function(){
            if(!this._workassignmentFieldSet)
                this._workassignmentFieldSet = this._factoryFieldSet({title: 'Designações de Exercício', items:[this.getWorkassignment()], height: 350}, this.getWorkassignment());
            return this._workassignmentFieldSet;
        },

        getConcessionFieldSet: function(){
            if(!this._concessionFieldSet)
                this._concessionFieldSet = this._factoryFieldSet({title: 'Concessão', items:[this.getConcession()]}, this.getConcession());
            return this._concessionFieldSet;
        },

        getStabilizationFieldSet: function(){
            if(!this._stabilizationFieldSet)
                this._stabilizationFieldSet = this._factoryFieldSet({title: 'Estabilização', items:[this.getStabilization()]}, this.getStabilization());
            return this._stabilizationFieldSet;
        },

        getProgressionFieldSet: function(){
            if(!this._progressionFieldSet)
                this._progressionFieldSet = this._factoryFieldSet({title: 'Progressão', items:[this.getProgression()]}, this.getProgression());
            return this._progressionFieldSet;
        },

        getLegalframingFieldSet: function(){
            if(!this._legalframingFieldSet)
                this._legalframingFieldSet = this._factoryFieldSet({title: 'Enquadramento', items:[this.getLegalframing()]}, this.getLegalframing());
            return this._legalframingFieldSet;
        },

        getRedistributionFieldSet: function(){
            if(!this._redistributionFieldSet)
                this._redistributionFieldSet = this._factoryFieldSet({title: 'Redistribuição', items:[this.getRedistribution()]}, this.getRedistribution());
            return this._redistributionFieldSet;
        },

        getRequisitionFieldSet: function(){
            if(!this._requisitionFieldSet)
                this._requisitionFieldSet = this._factoryFieldSet({title: 'Requisição', items:[this.getRequisition()]}, this.getRequisition());
            return this._requisitionFieldSet;
        },

        getRemovalFieldSet: function(){
            if(!this._removalFieldSet)
                this._removalFieldSet = this._factoryFieldSet({title: 'Remoção', items:[this.getRemoval()]}, this.getRemoval());
            return this._removalFieldSet;
        },

        getDiligenceFieldSet: function(){
            if(!this._diligenceFieldSet)
                this._diligenceFieldSet = this._factoryFieldSet({title: 'Designação para Diligência', items:[this.getDiligence()]}, this.getDiligence());
            return this._diligenceFieldSet;
        },
        getAuxCoordenationFieldSet: function(){
            if(!this._aux_coordenationFieldSet)
                this._aux_coordenationFieldSet = this._factoryFieldSet({title: 'Designação para Auxiliar de Coordenação', items:[this.getAuxCoordenation()]}, this.getAuxCoordenation());
            return this._aux_coordenationFieldSet;
        },

        getTeletrabalhoFieldSet: function(){
            if(!this._teletrabalhoFieldSet)
                this._teletrabalhoFieldSet = this._factoryFieldSet({title: 'Teletrabalho', items:[this.getTeletrabalho()]}, this.getTeletrabalho());
            return this._teletrabalhoFieldSet;
        },

        getWorkplace: function() {
            if(!this._workplaceGrid){
                this._workplaceGrid = this._factoryGrid('rh.employee.workplace.managerbyemployee.WorkplaceGrid', {});
                this._workplaceGrid.setFilterProperty('designacao', false, 1, false);
            }
            return this._workplaceGrid;
        },

        getWorkassignment: function() {
            if(!this._workassignment){
                this._workassignment = this._factoryGrid('rh.employee.workplace.managerbyemployee.WorkassignmentGrid', {});
                this._workassignment.setParam('designacao', true);
                this._workassignment.setFilterProperty('designacao', true, 1, false);
            }
            return this._workassignment;
        },

        getConcession: function() {
            if(!this._concession)
                this._concession = this._factoryGrid('rh.movimentacao.concession.Grid', {});
            return this._concession;
        },

        getStabilization: function() {
            if(!this._stabilization)
                this._stabilization = this._factoryGrid('rh.movimentacao.stabilization.Grid', {
                    hideItemsToolbar: ['add', 'remove'],
                    hideActions: ['add', 'remove', 'copy']
                });
            return this._stabilization;
        },

        getProgression: function() {
            if(!this._progression)
                this._progression = this._factoryGrid('rh.movimentacao.progression.Grid', {});
            return this._progression;
        },

        getLegalframing: function() {
            if(!this._legalframing)
                this._legalframing = this._factoryGrid('rh.movimentacao.progression.legalframing.Grid', {});
            return this._legalframing;
        },

        getRedistribution: function() {
            if(!this._redistribution)
                this._redistribution = this._factoryGrid('rh.movimentacao.redistribution.Grid', {});
            return this._redistribution;
        },

        getRequisition: function() {
            if(!this._requisition)
                this._requisition = this._factoryGrid('rh.movimentacao.requisicao.Grid', {});
            return this._requisition;
        },

        getRemoval: function() {
            if(!this._removal)
                this._removal = this._factoryGrid('rh.movimentacao.removal.Grid', {});
            return this._removal;
        },

        getDiligence: function() {
            if(!this._diligence)
                this._diligence = this._factoryGrid('rh.movimentacao.diligence.Grid', {});
            return this._diligence;
        },
        
        getAuxCoordenation: function() {
            if(!this._aux_coordenation)
                this._aux_coordenation = this._factoryGrid('rh.movimentacao.aux_coordenation.Grid', {
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                    hideActions: ['add', 'remove', 'edit', 'copy']
                });
            return this._aux_coordenation;
        },

        getTeletrabalho: function() {
            if(!this._teletrabalho)
                this._teletrabalho = this._factoryGrid('rh.movimentacao.teletrabalho.Grid', {});
            return this._teletrabalho;
        },
    }
);
