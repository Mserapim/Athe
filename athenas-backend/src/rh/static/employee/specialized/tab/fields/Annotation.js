rh.employee.specialized.tab.fields.Annotation = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Annotation.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function(){
            rh.employee.specialized.tab.fields.Annotation.superclass.observerEmployeePk.call(this, {});
            this.getAnnotationDepartureFieldSet().collapse(false);
            this.getAnnotationAbsenceFieldSet().collapse(false);
            this.getAnnotationCommunicationFieldSet().collapse(false);
            this.getAnnotationPraiseFieldSet().collapse(false);
            this.getAnnotationCareerFieldSet().collapse(false);
            this.getAnnotationEventFieldSet().collapse(false);
            this.getAnnotationLackFieldSet().collapse(false);
            this.getAnnotationVacationFieldSet().collapse(false);
            this.getAnnotationBirthdayBreakFieldSet().collapse(false);
            this.getAnnotationBalanceSheetFieldSet().collapse(false);
            this.getAnnotationElectoralSlackFieldSet().collapse(false);
            this.getAnnotationGeneralFieldSet().collapse(false);
            this.getAnnotationGratuityFieldSet().collapse(false);
            this.getAnnotationSpecialTimeFieldSet().collapse(false);
            this.getAnnotationLicenseFieldSet().collapse(false);
            this.getAnnotationDisciplinaryFieldSet().collapse(false);
            this.getAnnotationRecessFieldSet().collapse(false);
            this.getAnnotationRemovalFieldSet().collapse(false);
            this.getAnnotationDoubleTimeFieldSet().collapse(false);
            this.getAnnotationTimeServiceFieldSet().collapse(false);
            this.getAnnotationTranspositionFieldSet().collapse(false);
            this.getAnnotationTravelFieldSet().collapse(false);
            this.getAnnotationElectoralFieldSet().collapse(false);
        },

        fields: function(cfg){
            var items = [
                this.getAnnotationDepartureFieldSet(),
                this.getAnnotationAbsenceFieldSet(),
                this.getAnnotationCommunicationFieldSet(),
                this.getAnnotationPraiseFieldSet(),
                this.getAnnotationCareerFieldSet(),
                this.getAnnotationEventFieldSet(),
                this.getAnnotationLackFieldSet(),
                this.getAnnotationVacationFieldSet(),
                this.getAnnotationBirthdayBreakFieldSet(),
                this.getAnnotationBalanceSheetFieldSet(),
                this.getAnnotationElectoralSlackFieldSet(),
                this.getAnnotationGeneralFieldSet(),
                this.getAnnotationGratuityFieldSet(),
                this.getAnnotationSpecialTimeFieldSet(),
                this.getAnnotationLicenseFieldSet(),
                this.getAnnotationDisciplinaryFieldSet(),
                this.getAnnotationRecessFieldSet(),
                this.getAnnotationRemovalFieldSet(),
                this.getAnnotationDoubleTimeFieldSet(),
                this.getAnnotationTimeServiceFieldSet(),
                this.getAnnotationTranspositionFieldSet(),
                this.getAnnotationTravelFieldSet(),
                this.getAnnotationElectoralFieldSet(),
            ];
            return items;
        },

        getAnnotationDepartureFieldSet: function(){
            if(!this._annotationDepartureFieldSet)
                this._annotationDepartureFieldSet = this._factoryFieldSet({title: 'Anotação Afastamento', items:[this.getAnnotationDeparture()]}, this.getAnnotationDeparture());
            return this._annotationDepartureFieldSet;
        },

        getAnnotationAbsenceFieldSet: function(){
            if(!this._annotationAbsenceFieldSet)
                this._annotationAbsenceFieldSet = this._factoryFieldSet({title: 'Anotação Ausência', items:[this.getAnnotationAbsence()]}, this.getAnnotationAbsence());
            return this._annotationAbsenceFieldSet;
        },

        getAnnotationCommunicationFieldSet: function(){
            if(!this._annotationCommunicationFieldSet)
                this._annotationCommunicationFieldSet = this._factoryFieldSet({title: 'Anotação Comunicação', items:[this.getAnnotationCommunication()]}, this.getAnnotationCommunication());
            return this._annotationCommunicationFieldSet;
        },

        getAnnotationPraiseFieldSet: function(){
            if(!this._annotationPraiseFieldSet)
                this._annotationPraiseFieldSet = this._factoryFieldSet({title: 'Anotação Elogio', items:[this.getAnnotationPraise()]}, this.getAnnotationPraise());
            return this._annotationPraiseFieldSet;
        },

        getAnnotationCareerFieldSet: function(){
            if(!this._annotationCareerFieldSet)
                this._annotationCareerFieldSet = this._factoryFieldSet({title: 'Anotação Carreira', items:[this.getAnnotationCareer()]}, this.getAnnotationCareer());
            return this._annotationCareerFieldSet;
        },

        getAnnotationEventFieldSet: function(){
            if(!this._annotationEventFieldSet)
                this._annotationEventFieldSet = this._factoryFieldSet({title: 'Anotação Evento', items:[this.getAnnotationEvent()]}, this.getAnnotationEvent());
            return this._annotationEventFieldSet;
        },

        getAnnotationLackFieldSet: function(){
            if(!this._annotationLackFieldSet)
                this._annotationLackFieldSet = this._factoryFieldSet({title: 'Anotação Falta', items:[this.getAnnotationLack()]}, this.getAnnotationLack());
            return this._annotationLackFieldSet;
        },

        getAnnotationVacationFieldSet: function(){
            if(!this._annotationVacationFieldSet)
                this._annotationVacationFieldSet = this._factoryFieldSet({title: 'Anotação Férias', items:[this.getAnnotationVacation()]}, this.getAnnotationVacation());
            return this._annotationVacationFieldSet;
        },

        getAnnotationBirthdayBreakFieldSet: function(){
            if(!this._annotationBirthdayBreakFieldSet)
                this._annotationBirthdayBreakFieldSet = this._factoryFieldSet({title: 'Anotação Folga Aniversário', items:[this.getAnnotationBirthdayBreak()]}, this.getAnnotationBirthdayBreak());
            return this._annotationBirthdayBreakFieldSet;
        },

        getAnnotationBalanceSheetFieldSet: function(){
            if(!this._annotationBalanceSheetFieldSet)
                this._annotationBalanceSheetFieldSet = this._factoryFieldSet({title: 'Anotação Folga Compensação', items:[this.getAnnotationBalanceSheet()]}, this.getAnnotationBalanceSheet());
            return this._annotationBalanceSheetFieldSet;
        },

        getAnnotationElectoralSlackFieldSet: function(){
            if(!this._annotationElectoralSlackFieldSet)
                this._annotationElectoralSlackFieldSet = this._factoryFieldSet({title: 'Anotação Folga Eleitoral', items:[this.getAnnotationElectoralSlack()]}, this.getAnnotationElectoralSlack());
            return this._annotationElectoralSlackFieldSet;
        },

        getAnnotationGeneralFieldSet: function(){
            if(!this._annotationGeneralFieldSet)
                this._annotationGeneralFieldSet = this._factoryFieldSet({title: 'Anotação Geral', items:[this.getAnnotationGeneral()]}, this.getAnnotationGeneral());
            return this._annotationGeneralFieldSet;
        },

        getAnnotationGratuityFieldSet: function(){
            if(!this._annotationGratuityFieldSet)
                this._annotationGratuityFieldSet = this._factoryFieldSet({title: 'Anotação Gratificação', items:[this.getAnnotationGratuity()]}, this.getAnnotationGratuity());
            return this._annotationGratuityFieldSet;
        },

        getAnnotationSpecialTimeFieldSet: function(){
            if(!this._annotationSpecialTimeFieldSet)
                this._annotationSpecialTimeFieldSet = this._factoryFieldSet({title: 'Anotação Horário Especial', items:[this.getAnnotationSpecialTime()]}, this.getAnnotationSpecialTime());
            return this._annotationSpecialTimeFieldSet;
        },

        getAnnotationLicenseFieldSet: function(){
            if(!this._annotationLicenseFieldSet)
                this._annotationLicenseFieldSet = this._factoryFieldSet({title: 'Anotação Licença', items:[this.getAnnotationLicense()]}, this.getAnnotationLicense());
            return this._annotationLicenseFieldSet;
        },

        getAnnotationDisciplinaryFieldSet: function(){
            if(!this._annotationDisciplinaryFieldSet)
                this._annotationDisciplinaryFieldSet = this._factoryFieldSet({title: 'Anotação Pena Disciplinar', items:[this.getAnnotationDisciplinary()]}, this.getAnnotationDisciplinary());
            return this._annotationDisciplinaryFieldSet;
        },

        getAnnotationRecessFieldSet: function(){
            if(!this._annotationRecessFieldSet)
                this._annotationRecessFieldSet = this._factoryFieldSet({title: 'Anotação Recesso', items:[this.getAnnotationRecess()]}, this.getAnnotationRecess());
            return this._annotationRecessFieldSet;
        },

        getAnnotationRemovalFieldSet: function(){
            if(!this._annotationRemovalFieldSet)
                this._annotationRemovalFieldSet = this._factoryFieldSet({title: 'Anotação Remoção', items:[this.getAnnotationRemoval()]}, this.getAnnotationRemoval());
            return this._annotationRemovalFieldSet;
        },

        getAnnotationDoubleTimeFieldSet: function(){
            if(!this._annotationDoubleTimeFieldSet)
                this._annotationDoubleTimeFieldSet = this._factoryFieldSet({title: 'Anotação Tempo Dobro', items:[this.getAnnotationDoubleTime()]}, this.getAnnotationDoubleTime());
            return this._annotationDoubleTimeFieldSet;
        },

        getAnnotationTimeServiceFieldSet: function(){
            if(!this._annotationTimeServiceFieldSet)
                this._annotationTimeServiceFieldSet = this._factoryFieldSet({title: 'Anotação Tempo Serviço/Contribuição', items:[this.getAnnotationTimeService()]}, this.getAnnotationTimeService());
            return this._annotationTimeServiceFieldSet;
        },

        getAnnotationTranspositionFieldSet: function(){
            if(!this._annotationTranspositionFieldSet)
                this._annotationTranspositionFieldSet = this._factoryFieldSet({title: 'Anotação Transposição', items:[this.getAnnotationTransposition()]}, this.getAnnotationTransposition());
            return this._annotationTranspositionFieldSet;
        },

        getAnnotationTravelFieldSet: function(){
            if(!this._annotationTravelFieldSet)
                this._annotationTravelFieldSet = this._factoryFieldSet({title: 'Anotação Viagem', items:[this.getAnnotationTravel()]}, this.getAnnotationTravel());
            return this._annotationTravelFieldSet;
        },

        getAnnotationElectoralFieldSet: function(){
            if(!this._annotationElectoralFieldSet)
                this._annotationElectoralFieldSet = this._factoryFieldSet({title: 'Anotação de Declínio Eleitoral', items:[this.getAnnotationElectoral()]}, this.getAnnotationElectoral());
            return this._annotationElectoralFieldSet;
        },

        getAnnotationDeparture: function() {
            if(!this._anotacaoafastamento)
                this._anotacaoafastamento = this._factoryGrid('rh.anotacao.anotacaoafastamento.Grid', {});
            return this._anotacaoafastamento;
        },

        getAnnotationAbsence: function() {
            if(!this._anotacaoausencia)
                this._anotacaoausencia = this._factoryGrid('rh.anotacao.anotacaoausencia.Grid', {});
            return this._anotacaoausencia;
        },

        getAnnotationCommunication: function() {
            if(!this._anotacaocomunicacao)
                this._anotacaocomunicacao = this._factoryGrid('rh.anotacao.anotacaocomunicacao.Grid', {});
            return this._anotacaocomunicacao;
        },

        getAnnotationPraise: function() {
            if(!this._anotacaoelogio)
                this._anotacaoelogio = this._factoryGrid('rh.anotacao.anotacaoelogio.Grid', {});
            return this._anotacaoelogio;
        },

        getAnnotationCareer: function() {
            if(!this._anotacaocarreira)
                this._anotacaocarreira = this._factoryGrid('rh.anotacao.anotacaocarreira.Grid', {});
            return this._anotacaocarreira;
        },

        getAnnotationEvent: function() {
            if(!this._anotacaoevento)
                this._anotacaoevento = this._factoryGrid('rh.anotacao.anotacaoevento.Grid', {});
            return this._anotacaoevento;
        },

        getAnnotationLack: function() {
            if(!this._anotacaofalta)
                this._anotacaofalta = this._factoryGrid('rh.anotacao.anotacaofalta.Grid', {});
            return this._anotacaofalta;
        },

        getAnnotationVacation: function() {
            if(!this._anotacaoferias)
                this._anotacaoferias = this._factoryGrid('rh.anotacao.anotacaoferias.Grid', {});
            return this._anotacaoferias;
        },

        getAnnotationBirthdayBreak: function() {
            if(!this._anotacaofolgaaniversario)
                this._anotacaofolgaaniversario = this._factoryGrid('rh.anotacao.anotacaofolgaaniversario.Grid', {});
            return this._anotacaofolgaaniversario;
        },

        getAnnotationBalanceSheet: function() {
            if(!this._anotacaofolgacompensacao)
                this._anotacaofolgacompensacao = this._factoryGrid('rh.anotacao.anotacaofolgacompensacao.Grid', {});
            return this._anotacaofolgacompensacao;
        },

        getAnnotationElectoralSlack: function() {
            if(!this._anotacaofolgaeleitoral)
                this._anotacaofolgaeleitoral = this._factoryGrid('rh.anotacao.anotacaofolgaeleitoral.Grid', {});
            return this._anotacaofolgaeleitoral;
        },

        getAnnotationGeneral: function() {
            if(!this._anotacaogeral)
                this._anotacaogeral = this._factoryGrid('rh.anotacao.anotacaogeral.Grid', {});
            return this._anotacaogeral;
        },

        getAnnotationGratuity: function() {
            if(!this._anotacaogratificacao)
                this._anotacaogratificacao = this._factoryGrid('rh.anotacao.anotacaogratificacao.Grid', {});
            return this._anotacaogratificacao;
        },

        getAnnotationSpecialTime: function() {
            if(!this._anotacaohorarioespecial)
                this._anotacaohorarioespecial = this._factoryGrid('rh.anotacao.anotacaohorarioespecial.Grid', {});
            return this._anotacaohorarioespecial;
        },

        getAnnotationLicense: function() {
            if(!this._anotacaolicenca)
                this._anotacaolicenca = this._factoryGrid('rh.anotacao.anotacaolicenca.Grid', {});
            return this._anotacaolicenca;
        },

        getAnnotationDisciplinary: function() {
            if(!this._anotacaopenadisciplinar)
                this._anotacaopenadisciplinar = this._factoryGrid('rh.anotacao.anotacaopenadisciplinar.Grid', {});
            return this._anotacaopenadisciplinar;
        },

        getAnnotationRecess: function() {
            if(!this._anotacaorecesso)
                this._anotacaorecesso = this._factoryGrid('rh.anotacao.anotacaorecesso.Grid', {});
            return this._anotacaorecesso;
        },

        getAnnotationRemoval: function() {
            if(!this._anotacaoremocao)
                this._anotacaoremocao = this._factoryGrid('rh.anotacao.anotacaoremocao.Grid', {});
            return this._anotacaoremocao;
        },

        getAnnotationDoubleTime: function() {
            if(!this._anotacaotempodobro)
                this._anotacaotempodobro = this._factoryGrid('rh.anotacao.anotacaotempodobro.Grid', {});
            return this._anotacaotempodobro;
        },

        getAnnotationTimeService: function() {
            if(!this._anotacaotemposervico)
                this._anotacaotemposervico = this._factoryGrid('rh.anotacao.anotacaotemposervico.Grid', {});
            return this._anotacaotemposervico;
        },

        getAnnotationTransposition: function() {
            if(!this._anotacaotransposicao)
                this._anotacaotransposicao = this._factoryGrid('rh.anotacao.anotacaotransposicao.Grid', {});
            return this._anotacaotransposicao;
        },

        getAnnotationTravel: function() {
            if(!this._anotacaoviagem)
                this._anotacaoviagem = this._factoryGrid('rh.anotacao.anotacaoviagem.Grid', {});
            return this._anotacaoviagem;
        },

        getAnnotationElectoral: function() {
            if(!this._anotacaoeleitoral)
                this._anotacaoeleitoral = this._factoryGrid('rh.anotacao.anotacaoeleitoral.Grid', {});
            return this._anotacaoeleitoral;
        },
    }
);
