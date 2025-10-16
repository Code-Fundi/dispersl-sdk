/**
 * Comprehensive unit tests for serializers
 */

import { JSONSerializer, NDJSONParser, StreamParser, SerializationError } from '../../src/serializers';

describe('JSONSerializer', () => {
  describe('Serialization', () => {
    test('should serialize object', () => {
      const data = { key: 'value', number: 42 };
      const result = JSONSerializer.serialize(data);
      expect(result).toBe('{"key":"value","number":42}');
    });

    test('should serialize array', () => {
      const data = [1, 2, 3, 'test'];
      const result = JSONSerializer.serialize(data);
      expect(result).toBe('[1,2,3,"test"]');
    });

    test('should serialize nested structures', () => {
      const data = {
        user: { name: 'John', age: 30 },
        items: [1, 2, 3],
        active: true
      };
      const result = JSONSerializer.serialize(data);
      const parsed = JSON.parse(result);
      expect(parsed).toEqual(data);
    });

    test('should serialize null', () => {
      const result = JSONSerializer.serialize(null);
      expect(result).toBe('null');
    });

    test('should serialize with indentation', () => {
      const data = { key: 'value' };
      const result = JSONSerializer.serialize(data, { indent: 2 });
      expect(result).toContain('  ');
    });
  });

  describe('Deserialization', () => {
    test('should deserialize object', () => {
      const json = '{"key":"value","number":42}';
      const result = JSONSerializer.deserialize(json);
      expect(result).toEqual({ key: 'value', number: 42 });
    });

    test('should deserialize array', () => {
      const json = '[1,2,3,"test"]';
      const result = JSONSerializer.deserialize(json);
      expect(result).toEqual([1, 2, 3, 'test']);
    });

    test('should throw error on invalid JSON', () => {
      expect(() => JSONSerializer.deserialize('{invalid json')).toThrow(SerializationError);
    });

    test('should throw error on empty string', () => {
      expect(() => JSONSerializer.deserialize('')).toThrow(SerializationError);
    });

    test('should handle round trip', () => {
      const original = { nested: { data: [1, 2, 3] }, flag: true };
      const serialized = JSONSerializer.serialize(original);
      const deserialized = JSONSerializer.deserialize(serialized);
      expect(deserialized).toEqual(original);
    });
  });
});

describe('NDJSONParser', () => {
  describe('Parsing', () => {
    test('should parse single line', () => {
      const ndjson = '{"type":"message","content":"Hello"}\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(1);
      expect(results[0]).toEqual({ type: 'message', content: 'Hello' });
    });

    test('should parse multiple lines', () => {
      const ndjson = '{"id":1,"text":"First"}\n{"id":2,"text":"Second"}\n{"id":3,"text":"Third"}\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(3);
      expect(results[0].id).toBe(1);
      expect(results[1].id).toBe(2);
      expect(results[2].id).toBe(3);
    });

    test('should handle empty lines', () => {
      const ndjson = '{"id":1}\n\n{"id":2}\n\n\n{"id":3}\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(3);
    });

    test('should handle whitespace', () => {
      const ndjson = '  {"id":1}  \n\t{"id":2}\t\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(2);
    });

    test('should skip invalid JSON lines', () => {
      const ndjson = '{"valid":true}\n{invalid json}\n{"also_valid":true}\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      // Should skip invalid line
      expect(results.length).toBe(2);
    });

    test('should parse nested objects', () => {
      const ndjson = '{"user":{"name":"John","age":30},"active":true}\n{"data":[1,2,3],"meta":{"count":3}}\n';
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(2);
      expect(results[0].user.name).toBe('John');
      expect(results[1].data).toEqual([1, 2, 3]);
    });

    test('should parse agent step response', () => {
      const ndjson = 
        '{"type":"step_start","step_id":"step_123"}\n' +
        '{"type":"content","delta":"Hello"}\n' +
        '{"type":"content","delta":" world"}\n' +
        '{"type":"tool_call","name":"search","args":{"query":"test"}}\n' +
        '{"type":"step_complete","step_id":"step_123"}\n';
      
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(ndjson));
      
      expect(results.length).toBe(5);
      expect(results[0].type).toBe('step_start');
      expect(results[1].delta).toBe('Hello');
      expect(results[3].type).toBe('tool_call');
      expect(results[4].type).toBe('step_complete');
    });

    test('should handle empty string', () => {
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse(''));
      
      expect(results.length).toBe(0);
    });

    test('should handle only whitespace', () => {
      const parser = new NDJSONParser();
      const results = Array.from(parser.parse('\n\n  \n\t\n'));
      
      expect(results.length).toBe(0);
    });
  });
});

describe('StreamParser', () => {
  describe('Chunk Parsing', () => {
    test('should parse complete chunks', async () => {
      const chunks = [
        Buffer.from('{"id":1}\n'),
        Buffer.from('{"id":2}\n'),
        Buffer.from('{"id":3}\n')
      ];
      
      const parser = new StreamParser();
      const results: any[] = [];
      
      for (const chunk of chunks) {
        for (const parsed of parser.parseChunk(chunk)) {
          results.push(parsed);
        }
      }
      
      expect(results.length).toBe(3);
      expect(results[0].id).toBe(1);
    });

    test('should handle incomplete chunks', async () => {
      const parser = new StreamParser();
      
      const chunk1 = Buffer.from('{"message":"Hello ');
      const chunk2 = Buffer.from('World","id"');
      const chunk3 = Buffer.from(':1}\n');
      
      const results1 = Array.from(parser.parseChunk(chunk1));
      const results2 = Array.from(parser.parseChunk(chunk2));
      const results3 = Array.from(parser.parseChunk(chunk3));
      
      expect(results1.length).toBe(0);
      expect(results2.length).toBe(0);
      expect(results3.length).toBe(1);
      expect(results3[0].message).toBe('Hello World');
    });

    test('should parse multiple objects in one chunk', async () => {
      const chunk = Buffer.from('{"id":1}\n{"id":2}\n{"id":3}\n');
      const parser = new StreamParser();
      const results = Array.from(parser.parseChunk(chunk));
      
      expect(results.length).toBe(3);
      expect(results.map(r => r.id)).toEqual([1, 2, 3]);
    });

    test('should handle mixed complete and incomplete', async () => {
      const parser = new StreamParser();
      
      const chunk1 = Buffer.from('{"id":1}\n{"id":2}\n{"incomplete":');
      const chunk2 = Buffer.from('"value"}\n{"id":3}\n');
      
      const results1 = Array.from(parser.parseChunk(chunk1));
      const results2 = Array.from(parser.parseChunk(chunk2));
      
      expect(results1.length).toBe(2);
      expect(results2.length).toBe(2);
    });

    test('should handle UTF-8 encoding', async () => {
      const chunk = Buffer.from('{"message":"こんにちは"}\n', 'utf-8');
      const parser = new StreamParser('utf-8');
      const results = Array.from(parser.parseChunk(chunk));
      
      expect(results.length).toBe(1);
      expect(results[0].message).toBe('こんにちは');
    });

    test('should parse agent streaming response', async () => {
      const chunks = [
        Buffer.from('{"type":"step_start","step_id":"step_1"}\n'),
        Buffer.from('{"type":"content","delta":"I"}\n{"type":"content","delta":" am"}\n'),
        Buffer.from('{"type":"content","delta":" thinking"}\n'),
        Buffer.from('{"type":"tool_call","function":{"name":"search","arguments":"{\\"query\\":\\"test\\"}"}}\n'),
        Buffer.from('{"type":"step_complete","step_id":"step_1"}\n')
      ];
      
      const parser = new StreamParser();
      const allResults: any[] = [];
      
      for (const chunk of chunks) {
        for (const parsed of parser.parseChunk(chunk)) {
          allResults.push(parsed);
        }
      }
      
      expect(allResults.length).toBeGreaterThanOrEqual(5);
      expect(allResults.some(r => r.type === 'step_start')).toBe(true);
      expect(allResults.some(r => r.type === 'tool_call')).toBe(true);
      expect(allResults.some(r => r.type === 'step_complete')).toBe(true);
    });

    test('should handle large chunks', async () => {
      const largeData = { data: 'x'.repeat(10000), id: 1 };
      const chunk = Buffer.from(JSON.stringify(largeData) + '\n');
      
      const parser = new StreamParser();
      const results = Array.from(parser.parseChunk(chunk));
      
      expect(results.length).toBe(1);
      expect(results[0].data.length).toBe(10000);
    });

    test('should flush buffer', async () => {
      const parser = new StreamParser();
      
      const chunk = Buffer.from('{"incomplete":"data"');
      Array.from(parser.parseChunk(chunk));
      
      const remaining = parser.flush();
      expect(remaining).toBeDefined();
    });

    test('should reset parser', async () => {
      const parser = new StreamParser();
      
      parser.parseChunk(Buffer.from('{"incomplete":'));
      parser.reset();
      
      const chunk = Buffer.from('{"id":1}\n');
      const results = Array.from(parser.parseChunk(chunk));
      
      expect(results.length).toBe(1);
      expect(results[0].id).toBe(1);
    });

    test('should handle error gracefully', async () => {
      const parser = new StreamParser();
      
      const chunk = Buffer.from('{invalid json}\n');
      const results = Array.from(parser.parseChunk(chunk));
      
      // Should handle gracefully
      expect(Array.isArray(results)).toBe(true);
    });
  });
});

describe('SerializationError', () => {
  test('should create error', () => {
    const error = new SerializationError('Test error');
    expect(error.message).toBe('Test error');
    expect(error.name).toBe('SerializationError');
  });

  test('should be instance of Error', () => {
    const error = new SerializationError('Test');
    expect(error instanceof Error).toBe(true);
    expect(error instanceof SerializationError).toBe(true);
  });

  test('should include stack trace', () => {
    const error = new SerializationError('Test');
    expect(error.stack).toBeDefined();
  });
});

