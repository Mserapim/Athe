import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'formatarNome',
    standalone: false
})
export class FormatarNomePipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return value;

    return value.toLowerCase().replace(/\w\S*/g, (word) => {
      const lowerWords = ['da', 'de', 'do', 'dos', 'e'];
      if (lowerWords.includes(word)) return word;
      return word.charAt(0).toUpperCase() + word.substr(1).toLowerCase();
    });
  }
}